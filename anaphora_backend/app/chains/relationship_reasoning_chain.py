"""Iteration 5 — relationship-level reasoning over reciprocal finalists.

Retrieval and semantic reranking decide which candidates deserve attention.
This chain interprets only that small, grounded finalist set: alignment,
complementarity, meaningful tensions, incompatibilities and reciprocal fit.
It never searches the candidate database and never invents evidence.
"""
from __future__ import annotations

from langchain_openai import ChatOpenAI

from ..config import settings
from ..models import Candidate
from ..schemas import FitLevel, MatchExplanationsResult, MatchSection

RELATIONSHIP_REASONING_PROMPT = """You are Anaphora's relationship-level compatibility reasoner.
You receive a small finalist set that has already passed demographic eligibility, semantic retrieval and reciprocal reranking. Do NOT re-search or rescue weak candidates.

Your job is to reason about the likely relationship fit using ONLY the structured Blueprints and grounded evidence supplied.

For each finalist, distinguish these ideas instead of collapsing them into generic similarity:
- ALIGNMENT: important needs/values/dynamics that genuinely line up.
- COMPLEMENTARITY: differences that could plausibly work well together because the evidence supports them. Never call a difference complementary just to sound positive.
- TENSION: a real difference or asymmetry worth exploring, but not necessarily disqualifying.
- INCOMPATIBILITY: evidence that an important need, hard requirement or relationship dynamic meaningfully conflicts.
- RECIPROCITY: whether each person appears to fit what the other is looking for.

Decision rules:
- has_genuine_match=false when the evidence is too thin, substantially one-sided, or contains a meaningful incompatibility that makes an introduction irresponsible.
- recommended_fit=strong_fit only when there is convincing reciprocal evidence across several important dimensions and no significant unresolved incompatibility.
- recommended_fit=worth_exploring when an introduction is still genuinely worthwhile but evidence is thinner, more asymmetric, or includes a real non-disqualifying tension.
- recommended_fit must be null when has_genuine_match=false.
- Absence of evidence is uncertainty, NOT incompatibility.
- A clear contradiction with an explicit hard requirement on either side is disqualifying.
- Do not produce compatibility percentages or expose internal scores.

EXPLANATION:
Write 1-4 concise, natural sections only when has_genuine_match=true. Explain the relationship-level reason for the introduction rather than listing matching traits. Use headings such as "Why this could work", "How you might meet each other", or "Something to explore" when appropriate. Every sentence must be traceable to supplied Blueprint evidence. Never invent a shared interest, personality trait, life circumstance, or relationship dynamic."""


def _format_signal(raw: dict) -> str:
    return (
        f"{raw.get('category', 'unknown')}: {raw.get('label', '')} "
        f"[{raw.get('strength', 'preference')}]"
        + (f" — evidence: {raw.get('evidence_text')}" if raw.get("evidence_text") else "")
    )


def _candidate_profile(candidate: Candidate, perspective: str) -> str:
    signals = [
        raw for raw in (candidate.signals or [])
        if raw.get("perspective", "ME") == perspective and raw.get("label")
    ]
    return "\n".join(f"- {_format_signal(raw)}" for raw in signals) or "- no evidence"


def assess_relationship_candidates(
    user_context: str,
    candidates: list[tuple[Candidate, list[str], bool]],
    user_hard_requirements: list[str] | None = None,
) -> dict[str, tuple[bool, FitLevel | None, list[MatchSection]]]:
    """Interpret reciprocal finalists and return grounded relationship verdicts."""
    if not candidates:
        return {}

    hard_block = "\n".join(f"- {item}" for item in (user_hard_requirements or [])) or "- none explicitly established"
    candidate_blocks = []
    for candidate, evidence, reciprocal_complete in candidates:
        evidence_block = "\n".join(f"- {item}" for item in evidence) or "- none"
        candidate_blocks.append(
            f"candidate_id: {candidate.id}\n"
            f"candidate self narrative: {candidate.narrative or '(none)'}\n"
            f"reciprocal profile complete: {'yes' if reciprocal_complete else 'no'}\n"
            f"CANDIDATE ME BLUEPRINT:\n{_candidate_profile(candidate, 'ME')}\n"
            f"CANDIDATE IDEAL_PARTNER BLUEPRINT:\n{_candidate_profile(candidate, 'IDEAL_PARTNER')}\n"
            f"PRECOMPUTED RECIPROCAL EVIDENCE:\n{evidence_block}"
        )

    llm = ChatOpenAI(model=settings.openai_model, temperature=0.15, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(MatchExplanationsResult)
    result = structured_llm.invoke([
        {"role": "system", "content": RELATIONSHIP_REASONING_PROMPT},
        {"role": "user", "content": (
            f"USER BLUEPRINT:\n{user_context}\n\n"
            f"USER EXPLICIT HARD REQUIREMENTS:\n{hard_block}\n\n"
            f"FINALISTS:\n\n" + "\n\n---\n\n".join(candidate_blocks)
        )},
    ])

    verdicts = {}
    for item in result.explanations:
        if not item.has_genuine_match:
            verdicts[item.candidate_id] = (False, None, [])
            continue
        fit = item.recommended_fit or FitLevel.worth_exploring
        verdicts[item.candidate_id] = (True, fit, item.sections)
    return verdicts
