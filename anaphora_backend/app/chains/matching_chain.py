"""
Operation C — evidence-first matching.

Iteration 3 keeps matching one-directional (the user's IDEAL_PARTNER against a
candidate's ME profile) but separates cheap broad retrieval from structured
semantic reranking and deep LLM judgment.

Pipeline:
  eligibility (gender/age) -> broad vector retrieval -> category/signal
  semantic reranking -> 6 finalists -> grounded LLM judgment -> surface 1.

The human-readable Blueprint narrative is no longer the primary retrieval
representation. Structured signals, their strength/confidence and evidence are.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.orm import Session

from ..config import settings
from ..models import BlueprintSignal, Candidate
from ..schemas import CandidateOut, FitLevel, MatchExplanationsResult, MatchOut, MatchSection

BROAD_RETRIEVAL_SIZE = 24
FINALIST_SIZE = 6
MAX_MATCHES_SHOWN = 1
SEMANTIC_SIGNAL_THRESHOLD = 0.58
STRONG_FIT_THRESHOLD = 0.69

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
The candidates have already passed eligibility, broad semantic retrieval and structured reranking.
Your job is NOT to rescue weak candidates. Decide whether there is genuinely enough evidence to introduce each finalist.

For EACH candidate:
- Set has_genuine_match=true only when the supplied evidence pairs support a specific, meaningful case.
- A candidate must be rejected if the supplied evidence shows a clear contradiction with one of the user's HARD REQUIREMENTS.
- Absence of evidence is not automatically a contradiction. Do not invent missing candidate traits.
- Prefer evidence across several important categories over one superficial overlap.
- Thin, generic or coincidental similarity is not enough.
- If there is nothing specific and real to say, set has_genuine_match=false and leave sections empty.
- When genuine, write 1-4 short natural sections in Anaphora's warm, intelligent voice.
- You may honestly name a supported tension under a heading such as "Something to explore".
- Every sentence must be traceable to the supplied candidate narrative or evidence pairs. Never invent facts.
- Never expose internal scores, embeddings, confidence numbers or friend-contributed commentary."""

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
    """Deterministic compatibility fallback retained for tests/legacy use.

    Iteration 3's actual reranker uses embeddings. This lexical function is
    still useful as a high-precision exact/paraphrase fallback and for obvious
    polarity protection.
    """
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
    """Structured semantic representation for one Blueprint signal."""
    label = getattr(signal, "label", None) if not isinstance(signal, dict) else signal.get("label")
    evidence = getattr(signal, "evidence_text", None) if not isinstance(signal, dict) else signal.get("evidence_text")
    category = getattr(signal, "category", None) if not isinstance(signal, dict) else signal.get("category")
    return " | ".join(part for part in [str(category or ""), str(label or ""), str(evidence or "")] if part)


def _profile_embedding_text(signals: list[BlueprintSignal]) -> str:
    """Broad retrieval representation built from structured evidence, not narrative."""
    lines = []
    for signal in signals:
        strength = signal.strength or "preference"
        lines.append(f"{signal.category}: {signal.label} [{strength}] {signal.evidence_text or ''}".strip())
    return "\n".join(lines)


def embed_text(text: str) -> list[float]:
    embedder = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
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
    """Cheap broad retrieval within hard demographic eligibility constraints."""
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
    """Legacy deterministic overlap helper retained as a safe fallback."""
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


def _signal_weight(signal: BlueprintSignal) -> float:
    return (
        CATEGORY_WEIGHTS.get(signal.category or "", 1.0)
        * STRENGTH_WEIGHTS.get(signal.strength or "preference", 1.0)
        * max(0.35, float(signal.confidence if signal.confidence is not None else 1.0))
    )


def semantic_rerank_candidates(
    retrieved: list[tuple[Candidate, float]],
    user_signals: list[BlueprintSignal],
    finalist_size: int = FINALIST_SIZE,
) -> list[tuple[Candidate, float, list[str]]]:
    """Rerank broad results by same-category semantic evidence.

    One batched embedding call covers all unique user/candidate atomic signals
    and category summaries. The score rewards strong evidence across important
    categories while keeping broad profile similarity as a small tie-breaker.
    Evidence strings are retained for the final LLM rather than exposing scores.
    """
    if not retrieved or not user_signals:
        return []

    user_by_category: dict[str, list[BlueprintSignal]] = defaultdict(list)
    for signal in user_signals:
        if signal.label and signal.category:
            user_by_category[signal.category].append(signal)

    candidate_by_category: dict[str, dict[str, list[dict]]] = {}
    all_texts: list[str] = []
    text_index: dict[str, int] = {}

    def add_text(text: str) -> None:
        if text and text not in text_index:
            text_index[text] = len(all_texts)
            all_texts.append(text)

    for signals in user_by_category.values():
        for signal in signals:
            add_text(_signal_text(signal))
        add_text(" ; ".join(_signal_text(s) for s in signals))

    for candidate, _ in retrieved:
        grouped: dict[str, list[dict]] = defaultdict(list)
        for raw in candidate.signals or []:
            if raw.get("label") and raw.get("category"):
                grouped[raw["category"]].append(raw)
                add_text(_signal_text(raw))
        for values in grouped.values():
            add_text(" ; ".join(_signal_text(s) for s in values))
        candidate_by_category[candidate.id] = grouped

    if not all_texts:
        return []

    embedder = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    vectors = embedder.embed_documents(all_texts)

    def vector(text: str) -> list[float]:
        return vectors[text_index[text]]

    reranked: list[tuple[Candidate, float, list[str]]] = []
    for candidate, broad_similarity in retrieved:
        grouped = candidate_by_category.get(candidate.id, {})
        weighted_total = 0.0
        weight_total = 0.0
        category_scores: list[float] = []
        evidence_pairs: list[str] = []

        for category, desired_signals in user_by_category.items():
            candidate_signals = grouped.get(category, [])
            if not candidate_signals:
                continue

            user_category_text = " ; ".join(_signal_text(s) for s in desired_signals)
            candidate_category_text = " ; ".join(_signal_text(s) for s in candidate_signals)
            category_similarity = max(0.0, _cosine(vector(user_category_text), vector(candidate_category_text)))
            category_scores.append(category_similarity)

            for desired in desired_signals:
                best = None
                best_similarity = -1.0
                for actual in candidate_signals:
                    # Embeddings notoriously place antonyms/negations near each
                    # other. Keep the deterministic polarity guard for obvious
                    # cases before accepting a semantic pair.
                    if _has_negation(desired.label or "") != _has_negation(actual.get("label", "")):
                        continue
                    sim = _cosine(vector(_signal_text(desired)), vector(_signal_text(actual)))
                    if sim > best_similarity:
                        best_similarity = sim
                        best = actual

                weight = _signal_weight(desired)
                weight_total += weight
                contribution = max(0.0, best_similarity) if best is not None else 0.0
                weighted_total += weight * contribution

                if best is not None and best_similarity >= SEMANTIC_SIGNAL_THRESHOLD:
                    evidence_pairs.append(
                        f"{category}: user wants '{desired.label}' ({desired.strength or 'preference'}); "
                        f"candidate evidence '{best.get('label')}'"
                    )

        atomic_score = weighted_total / weight_total if weight_total else 0.0
        category_score = sum(category_scores) / len(category_scores) if category_scores else 0.0
        # Structured evidence dominates. Broad vector similarity only helps
        # recall/tie-breaking after eligibility, rather than defining fit.
        score = 0.68 * atomic_score + 0.22 * category_score + 0.10 * broad_similarity
        reranked.append((candidate, score, evidence_pairs))

    reranked.sort(key=lambda item: item[1], reverse=True)
    return reranked[:finalist_size]


def judge_and_explain_candidates(
    user_context: str,
    candidates: list[tuple[Candidate, list[str]]],
    hard_requirements: list[str] | None = None,
) -> dict[str, tuple[bool, list[MatchSection]]]:
    if not candidates:
        return {}

    hard_block = "\n".join(f"- {item}" for item in (hard_requirements or [])) or "- none explicitly established"
    candidates_block = "\n\n".join(
        f"candidate_id: {c.id}\n"
        f"candidate's own narrative: {c.narrative or '(none)'}\n"
        f"grounded evidence pairs:\n" + ("\n".join(f"- {item}" for item in evidence) if evidence else "- none")
        for c, evidence in candidates
    )
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.2, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(MatchExplanationsResult)
    result = structured_llm.invoke([
        {"role": "system", "content": MATCH_SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Structured description of what the user wants:\n{user_context}\n\n"
            f"Explicit hard requirements:\n{hard_block}\n\nFinalists:\n{candidates_block}"
        )},
    ])
    return {
        item.candidate_id: (item.has_genuine_match, item.sections if item.has_genuine_match else [])
        for item in result.explanations
    }


def find_matches(
    db: Session,
    user_narrative: str,
    user_ideal_partner_signals: list[BlueprintSignal],
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> list[MatchOut]:
    """Return at most one high-quality introduction for the current user."""
    if not user_ideal_partner_signals:
        return []

    # The narrative is intentionally ignored for retrieval. It remains useful
    # to the product UI, but structured Blueprint evidence is the matching
    # source of truth after Iteration 2.
    query_text = _profile_embedding_text(user_ideal_partner_signals)
    query_embedding = embed_text(query_text)
    retrieved = retrieve_candidates(
        db,
        query_embedding,
        k=BROAD_RETRIEVAL_SIZE,
        gender_preference=gender_preference,
        age_min=age_min,
        age_max=age_max,
    )
    finalists = semantic_rerank_candidates(retrieved, user_ideal_partner_signals, FINALIST_SIZE)

    structured_user_context = _profile_embedding_text(user_ideal_partner_signals)
    hard_requirements = [
        f"{s.category}: {s.label}"
        for s in user_ideal_partner_signals
        if s.strength == "hard_requirement" and (s.confidence is None or s.confidence >= 0.70)
    ]
    judged = judge_and_explain_candidates(
        structured_user_context,
        [(candidate, evidence) for candidate, _score, evidence in finalists],
        hard_requirements=hard_requirements,
    )

    genuine = [
        (candidate, score, evidence, sections)
        for candidate, score, evidence in finalists
        for has_genuine, sections in [judged.get(candidate.id, (False, []))]
        if has_genuine and sections
    ][:MAX_MATCHES_SHOWN]

    return [
        MatchOut(
            candidate=CandidateOut.model_validate(candidate),
            fit=(
                FitLevel.strong_fit
                if score >= STRONG_FIT_THRESHOLD and len(evidence) >= 3
                else FitLevel.worth_exploring
            ),
            sections=sections,
        )
        for candidate, score, evidence, sections in genuine
    ]
