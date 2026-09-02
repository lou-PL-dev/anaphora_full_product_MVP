"""
Operation C — reciprocal evidence-first matching.

Iteration 4 evaluates both directions:
  MY IDEAL_PARTNER -> CANDIDATE ME
  MY ME -> CANDIDATE IDEAL_PARTNER

This module owns eligibility, broad retrieval on the user's IDEAL_PARTNER,
and reciprocal semantic reranking down to a handful of finalists. The final
grounded judgment that turns finalists into a surfaced introduction lives in
matching_chain_v5.py (via relationship_reasoning_chain) — see that module
for the live orchestration. judge_and_explain_candidates() below is the
original Iteration 4 judgment step, kept and tested as a standalone scorer.

The two directional scores remain visible to the internal ranking logic rather
than being flattened into a naive average. A candidate who fits the user very
well but wants someone quite different is deliberately penalized.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict

from sqlalchemy.orm import Session

from ..llm import get_chat_llm, get_embedder
from ..models import BlueprintSignal, Candidate
from ..schemas import MatchExplanationsResult, MatchSection

BROAD_RETRIEVAL_SIZE = 24
FINALIST_SIZE = 6
MAX_MATCHES_SHOWN = 1
SEMANTIC_SIGNAL_THRESHOLD = 0.58
STRONG_FIT_THRESHOLD = 0.68
MIN_RECIPROCAL_DIRECTION_SCORE = 0.48
LEGACY_RECIPROCITY_PENALTY = 0.82

CATEGORY_WEIGHTS = {
    "personality": 1.15,
    "lifestyle": 1.10,
    "physical_type": 0.85,
    "relationship_dynamic": 1.25,
    "love_language": 0.95,
    "dealbreakers": 1.25,
    "values": 1.15,
}
STRENGTH_WEIGHTS = {
    "hard_requirement": 1.55,
    "strong_preference": 1.30,
    "preference": 1.00,
    "unknown": 0.75,
}

MATCH_SYSTEM_PROMPT = """You are the final grounded judge for Anaphora introductions.
The finalists have already passed eligibility, semantic retrieval and RECIPROCAL reranking.

You are given evidence in two distinct directions:
1. USER WANTS -> CANDIDATE IS: how the candidate fits what the user wants.
2. CANDIDATE WANTS -> USER IS: how the user fits what the candidate wants.

For EACH candidate:
- Set has_genuine_match=true only if there is enough specific evidence for a meaningful introduction.
- Reciprocity matters. Strong evidence in one direction must not hide clearly weak or contradictory evidence in the other.
- A clear contradiction with an explicit hard requirement on either side is grounds for rejection.
- Absence of evidence is not automatically a contradiction; never invent missing traits.
- Prefer several grounded dimensions over one superficial overlap.
- If the candidate lacks a reciprocal IDEAL_PARTNER profile, treat that as lower confidence, never as a strong reciprocal fit.
- When genuine, write 1-4 short natural sections in Anaphora's warm, intelligent voice.
- You may name a supported asymmetry or tension under "Something to explore".
- Every sentence must be traceable to supplied evidence or the candidate's own narrative.
- Never expose scores, embeddings, confidence numbers or internal ranking mechanics."""

_WORD_RE = re.compile(r"[a-z']+")
_LABEL_STOPWORDS = {
    "a", "an", "and", "or", "the", "of", "to", "in", "on", "for", "at", "with",
    "is", "are", "be", "being", "someone", "something", "person", "people",
    "their", "they", "them", "that", "this", "these", "those", "it", "its",
    "own", "very", "really", "quite", "much", "who", "who's",
}
_NEGATION_MARKERS = {
    "avoid", "avoids", "avoiding", "dislike", "dislikes", "hate", "hates",
    "refuse", "refuses", "not", "no", "never", "isn't", "aren't", "wasn't",
    "won't", "wouldn't", "can't", "cannot", "don't", "doesn't", "didn't",
    "without", "lack", "lacks", "lacking", "unwilling", "dealbreaker",
}


def _label_tokens(label: str) -> set[str]:
    words = _WORD_RE.findall((label or "").lower())
    return {w for w in words if w not in _LABEL_STOPWORDS and len(w) > 2}


def _has_negation(label: str) -> bool:
    return bool(_label_tokens(label) & _NEGATION_MARKERS)


def _labels_share_topic(a: str, b: str) -> bool:
    a_norm, b_norm = (a or "").strip().lower(), (b or "").strip().lower()
    if not a_norm or not b_norm:
        return False
    if a_norm == b_norm:
        return True
    a_tokens, b_tokens = _label_tokens(a_norm), _label_tokens(b_norm)
    if _has_negation(a_norm) != _has_negation(b_norm):
        return False
    overlap = a_tokens & b_tokens
    if len(overlap) < 2:
        return False
    return len(overlap) / max(1, min(len(a_tokens), len(b_tokens))) >= 0.5


def _signal_text(signal) -> str:
    label = getattr(signal, "label", None) if not isinstance(signal, dict) else signal.get("label")
    evidence = getattr(signal, "evidence_text", None) if not isinstance(signal, dict) else signal.get("evidence_text")
    category = getattr(signal, "category", None) if not isinstance(signal, dict) else signal.get("category")
    return " | ".join(part for part in [str(category or ""), str(label or ""), str(evidence or "")] if part)


def _profile_embedding_text(signals: list[BlueprintSignal]) -> str:
    lines = []
    for signal in signals:
        strength = signal.strength or "preference"
        lines.append(f"{signal.category}: {signal.label} [{strength}] {signal.evidence_text or ''}".strip())
    return "\n".join(lines)


def embed_text(text: str) -> list[float]:
    embedder = get_embedder()
    return embedder.embed_query(text)


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


def _normalise_gender_preference(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    aliases = {
        "man": "male", "men": "male", "male": "male",
        "woman": "female", "women": "female", "female": "female",
        "non-binary": "nonbinary", "nonbinary": "nonbinary", "non binary": "nonbinary",
    }
    return aliases.get(value, value)


def retrieve_candidates(
    db: Session,
    query_embedding: list[float],
    k: int = BROAD_RETRIEVAL_SIZE,
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> list[tuple[Candidate, float]]:
    query = db.query(Candidate, Candidate.embedding.cosine_distance(query_embedding).label("distance"))
    gender = _normalise_gender_preference(gender_preference)
    if gender and gender not in {"any", "all", "everyone"}:
        query = query.filter(Candidate.gender == gender)
    if age_min is not None:
        query = query.filter(Candidate.age >= age_min)
    if age_max is not None:
        query = query.filter(Candidate.age <= age_max)
    rows = query.order_by("distance").limit(k).all()
    return [(candidate, max(0.0, min(1.0, 1.0 - distance))) for candidate, distance in rows]


def shared_signals(user_ideal_partner_signals: list[BlueprintSignal], candidate_signals: list[dict]) -> list[str]:
    candidate_labels = [c["label"] for c in candidate_signals if c.get("label")]
    matched: list[str] = []
    seen: set[str] = set()
    for signal in user_ideal_partner_signals:
        label = signal.label
        key = label.strip().lower() if label else ""
        if not key or key in seen:
            continue
        if any(_labels_share_topic(label, candidate_label) for candidate_label in candidate_labels):
            matched.append(label)
            seen.add(key)
    return matched


def _signal_weight(signal: BlueprintSignal | dict) -> float:
    if isinstance(signal, dict):
        category = signal.get("category") or ""
        strength = signal.get("strength") or "preference"
        confidence = signal.get("confidence")
    else:
        category = signal.category or ""
        strength = signal.strength or "preference"
        confidence = signal.confidence
    return (
        CATEGORY_WEIGHTS.get(category, 1.0)
        * STRENGTH_WEIGHTS.get(strength, 1.0)
        * max(0.35, float(confidence if confidence is not None else 1.0))
    )


def _group_by_category(signals: list) -> dict[str, list]:
    grouped: dict[str, list] = defaultdict(list)
    for signal in signals:
        category = signal.get("category") if isinstance(signal, dict) else signal.category
        label = signal.get("label") if isinstance(signal, dict) else signal.label
        if category and label:
            grouped[category].append(signal)
    return grouped


def _candidate_signals(candidate: Candidate, perspective: str) -> list[dict]:
    result = []
    for raw in candidate.signals or []:
        raw_perspective = raw.get("perspective", "ME")
        if raw_perspective == perspective:
            result.append(raw)
    return result


def _directional_score(
    desired_signals: list,
    actual_signals: list,
    vector,
) -> tuple[float, list[str]]:
    desired_by_category = _group_by_category(desired_signals)
    actual_by_category = _group_by_category(actual_signals)
    weighted_total = 0.0
    weight_total = 0.0
    category_scores: list[float] = []
    evidence_pairs: list[str] = []

    for category, desired_group in desired_by_category.items():
        actual_group = actual_by_category.get(category, [])
        if not actual_group:
            for desired in desired_group:
                weight_total += _signal_weight(desired)
            continue

        desired_category_text = " ; ".join(_signal_text(s) for s in desired_group)
        actual_category_text = " ; ".join(_signal_text(s) for s in actual_group)
        category_scores.append(max(0.0, _cosine(vector(desired_category_text), vector(actual_category_text))))

        for desired in desired_group:
            desired_label = desired.get("label", "") if isinstance(desired, dict) else desired.label or ""
            best = None
            best_similarity = -1.0
            for actual in actual_group:
                actual_label = actual.get("label", "") if isinstance(actual, dict) else actual.label or ""
                if _has_negation(desired_label) != _has_negation(actual_label):
                    continue
                sim = _cosine(vector(_signal_text(desired)), vector(_signal_text(actual)))
                if sim > best_similarity:
                    best_similarity = sim
                    best = actual

            weight = _signal_weight(desired)
            weight_total += weight
            weighted_total += weight * max(0.0, best_similarity if best is not None else 0.0)

            if best is not None and best_similarity >= SEMANTIC_SIGNAL_THRESHOLD:
                desired_strength = desired.get("strength", "preference") if isinstance(desired, dict) else desired.strength or "preference"
                desired_text = desired.get("label") if isinstance(desired, dict) else desired.label
                actual_text = best.get("label") if isinstance(best, dict) else best.label
                evidence_pairs.append(
                    f"{category}: wants '{desired_text}' ({desired_strength}); evidence '{actual_text}'"
                )

    atomic_score = weighted_total / weight_total if weight_total else 0.0
    category_score = sum(category_scores) / len(category_scores) if category_scores else 0.0
    return 0.78 * atomic_score + 0.22 * category_score, evidence_pairs


def _reciprocal_score(forward: float, reverse: float | None, broad_similarity: float) -> float:
    """Combine directions without hiding asymmetry behind a simple average.

    The weaker direction matters substantially. A high forward score cannot
    compensate for a poor reverse score. Legacy candidates without an
    IDEAL_PARTNER profile remain explorable but receive a confidence penalty.
    """
    if reverse is None:
        return (0.90 * forward + 0.10 * broad_similarity) * LEGACY_RECIPROCITY_PENALTY
    weaker = min(forward, reverse)
    stronger = max(forward, reverse)
    balance = 1.0 - abs(forward - reverse)
    return 0.55 * weaker + 0.25 * stronger + 0.10 * balance + 0.10 * broad_similarity


def semantic_rerank_candidates(
    retrieved: list[tuple[Candidate, float]],
    user_ideal_signals: list[BlueprintSignal],
    user_me_signals: list[BlueprintSignal] | None = None,
    finalist_size: int = FINALIST_SIZE,
) -> list[tuple[Candidate, float, float, float | None, list[str], bool]]:
    """Reciprocal reranking while preserving directional asymmetry."""
    if not retrieved or not user_ideal_signals:
        return []
    user_me_signals = user_me_signals or []

    all_texts: list[str] = []
    text_index: dict[str, int] = {}

    def add_text(text: str) -> None:
        if text and text not in text_index:
            text_index[text] = len(all_texts)
            all_texts.append(text)

    def add_signal_set(signals: list) -> None:
        for signal in signals:
            add_text(_signal_text(signal))
        for values in _group_by_category(signals).values():
            add_text(" ; ".join(_signal_text(s) for s in values))

    add_signal_set(user_ideal_signals)
    add_signal_set(user_me_signals)
    for candidate, _ in retrieved:
        add_signal_set(_candidate_signals(candidate, "ME"))
        add_signal_set(_candidate_signals(candidate, "IDEAL_PARTNER"))

    if not all_texts:
        return []

    embedder = get_embedder()
    vectors = embedder.embed_documents(all_texts)

    def vector(text: str) -> list[float]:
        return vectors[text_index[text]]

    reranked = []
    for candidate, broad_similarity in retrieved:
        candidate_me = _candidate_signals(candidate, "ME")
        candidate_ideal = _candidate_signals(candidate, "IDEAL_PARTNER")
        forward, forward_evidence = _directional_score(user_ideal_signals, candidate_me, vector)

        reciprocal_complete = bool(candidate_ideal and user_me_signals)
        if reciprocal_complete:
            reverse, reverse_evidence = _directional_score(candidate_ideal, user_me_signals, vector)
        else:
            reverse, reverse_evidence = None, []

        score = _reciprocal_score(forward, reverse, broad_similarity)
        evidence = [f"USER WANTS -> CANDIDATE IS: {item}" for item in forward_evidence]
        evidence.extend(f"CANDIDATE WANTS -> USER IS: {item}" for item in reverse_evidence)
        reranked.append((candidate, score, forward, reverse, evidence, reciprocal_complete))

    reranked.sort(key=lambda item: item[1], reverse=True)
    return reranked[:finalist_size]


def judge_and_explain_candidates(
    user_context: str,
    candidates: list[tuple[Candidate, list[str], bool]],
    hard_requirements: list[str] | None = None,
) -> dict[str, tuple[bool, list[MatchSection]]]:
    if not candidates:
        return {}

    hard_block = "\n".join(f"- {item}" for item in (hard_requirements or [])) or "- none explicitly established"
    candidates_block = "\n\n".join(
        f"candidate_id: {candidate.id}\n"
        f"candidate's own narrative: {candidate.narrative or '(none)'}\n"
        f"reciprocal profile complete: {'yes' if reciprocal_complete else 'no'}\n"
        f"grounded reciprocal evidence:\n" + (
            "\n".join(f"- {item}" for item in evidence) if evidence else "- none"
        )
        for candidate, evidence, reciprocal_complete in candidates
    )
    llm = get_chat_llm(temperature=0.2)
    structured_llm = llm.with_structured_output(MatchExplanationsResult)
    result = structured_llm.invoke([
        {"role": "system", "content": MATCH_SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Structured description of the user:\n{user_context}\n\n"
            f"User hard requirements:\n{hard_block}\n\nFinalists:\n{candidates_block}"
        )},
    ])
    return {
        item.candidate_id: (item.has_genuine_match, item.sections if item.has_genuine_match else [])
        for item in result.explanations
    }
