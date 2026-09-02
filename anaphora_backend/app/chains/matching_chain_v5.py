"""Iteration 5 orchestration for relationship-level matching.

Iteration 4 remains responsible for eligibility, broad retrieval and reciprocal
semantic reranking. This module adds the final relationship reasoning layer and
keeps the public API unchanged.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import BlueprintSignal
from ..schemas import CandidateOut, FitLevel, MatchOut
from .matching_chain import (
    BROAD_RETRIEVAL_SIZE,
    FINALIST_SIZE,
    MAX_MATCHES_SHOWN,
    MIN_RECIPROCAL_DIRECTION_SCORE,
    STRONG_FIT_THRESHOLD,
    _profile_embedding_text,
    embed_text,
    retrieve_candidates,
    semantic_rerank_candidates,
)
from .relationship_reasoning_chain import assess_relationship_candidates


def find_matches(
    db: Session,
    user_narrative: str,
    user_ideal_partner_signals: list[BlueprintSignal],
    user_me_signals: list[BlueprintSignal] | None = None,
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> list[MatchOut]:
    """Return at most one introduction after relationship-level reasoning."""
    if not user_ideal_partner_signals:
        return []
    user_me_signals = user_me_signals or []

    # Cheap search still starts from MY IDEAL_PARTNER -> CANDIDATE ME.
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

    # Reciprocal semantic evidence narrows the pool before the expensive
    # relationship reasoner sees anything.
    finalists = semantic_rerank_candidates(
        retrieved,
        user_ideal_partner_signals,
        user_me_signals=user_me_signals,
        finalist_size=FINALIST_SIZE,
    )

    user_context = (
        "USER IDEAL_PARTNER:\n" + _profile_embedding_text(user_ideal_partner_signals)
        + "\n\nUSER ME:\n" + _profile_embedding_text(user_me_signals)
    )
    user_hard_requirements = [
        f"{signal.category}: {signal.label}"
        for signal in user_ideal_partner_signals
        if signal.strength == "hard_requirement"
        and (signal.confidence is None or signal.confidence >= 0.70)
    ]

    verdicts = assess_relationship_candidates(
        user_context,
        [
            (candidate, evidence, reciprocal_complete)
            for candidate, _score, _forward, _reverse, evidence, reciprocal_complete in finalists
        ],
        user_hard_requirements=user_hard_requirements,
    )

    genuine = []
    for candidate, score, forward, reverse, evidence, reciprocal_complete in finalists:
        has_match, model_fit, sections = verdicts.get(candidate.id, (False, None, []))
        if not has_match or not sections:
            continue

        # The reasoner interprets the relationship; deterministic gates remain
        # the final safety check for the strongest product label. This prevents
        # a persuasive explanation from upgrading a materially weak direction.
        strong_fit_allowed = (
            reciprocal_complete
            and reverse is not None
            and forward >= MIN_RECIPROCAL_DIRECTION_SCORE
            and reverse >= MIN_RECIPROCAL_DIRECTION_SCORE
            and score >= STRONG_FIT_THRESHOLD
            and len(evidence) >= 4
        )
        fit = (
            FitLevel.strong_fit
            if model_fit == FitLevel.strong_fit and strong_fit_allowed
            else FitLevel.worth_exploring
        )
        genuine.append((candidate, fit, sections))
        if len(genuine) >= MAX_MATCHES_SHOWN:
            break

    return [
        MatchOut(
            candidate=CandidateOut.model_validate(candidate),
            fit=fit,
            sections=sections,
        )
        for candidate, fit, sections in genuine
    ]
