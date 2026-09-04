"""Iteration 5 orchestration for relationship-level matching.

Iteration 4 remains responsible for eligibility, broad retrieval and reciprocal
semantic reranking. This module adds the final relationship reasoning layer.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from ..config import settings
from ..models import BlueprintSignal
from ..schemas import CandidateOut, FitLevel, MatchOut, MatchSection
from .matching_chain import (
    BROAD_RETRIEVAL_SIZE,
    FINALIST_SIZE,
    MIN_STRONG_EVIDENCE,
    MIN_WORTH_DIRECTION_SCORE,
    MIN_WORTH_EVIDENCE,
    MAX_MATCHES_SHOWN,
    MIN_RECIPROCAL_DIRECTION_SCORE,
    STRONG_FIT_THRESHOLD,
    WORTH_EXPLORING_THRESHOLD,
    _profile_embedding_text,
    candidate_accepts_user,
    embed_text,
    retrieve_candidates,
    semantic_rerank_candidates,
)
from .relationship_reasoning_chain import assess_relationship_candidates

logger = logging.getLogger(__name__)


def _demo_fixture_marker(candidate, user_id: str | None) -> dict | None:
    """Return only a fixture explicitly targeted to the current demo user."""
    if not user_id:
        return None
    for raw in candidate.signals or []:
        if (
            isinstance(raw, dict)
            and raw.get("kind") == "demo_fixture"
            and raw.get("target_user_id") == user_id
        ):
            return raw
    return None


def _candidate_available_for_user(candidate, user_id: str | None) -> bool:
    """Keep demo fixtures invisible outside their explicit opt-in scenario."""
    fixture_markers = [
        raw for raw in (candidate.signals or [])
        if isinstance(raw, dict) and raw.get("kind") == "demo_fixture"
    ]
    if not fixture_markers:
        return True
    return settings.anaphora_demo_mode and any(
        marker.get("target_user_id") == user_id for marker in fixture_markers
    )


def _demo_fallback_verdict(
    candidate,
    user_id: str | None,
    fit_ceiling: FitLevel | None,
) -> tuple[bool, FitLevel, list[MatchSection]] | None:
    """Grounded last resort for one opt-in synthetic demo fixture.

    The fixture must still pass normal retrieval, reciprocal demographics,
    semantic reranking, and the deterministic fit ceiling. This safeguard
    changes only the final LLM's ability to reject or omit that one fixture.
    """
    if not settings.anaphora_demo_mode or fit_ceiling is None:
        return None
    marker = _demo_fixture_marker(candidate, user_id)
    if marker is None:
        return None
    sections = []
    for raw in marker.get("fallback_sections") or []:
        try:
            sections.append(MatchSection.model_validate(raw))
        except Exception:
            continue
    if not sections:
        return None
    return True, fit_ceiling, sections


def _evidence_dimensions(evidence: list[str]) -> tuple[set[str], set[str]]:
    directions: set[str] = set()
    categories: set[str] = set()
    for item in evidence:
        direction, separator, rest = item.partition(": ")
        if not separator:
            continue
        category, category_separator, _detail = rest.partition(":")
        directions.add(direction)
        if category_separator and category:
            categories.add(category.strip())
    return directions, categories


def deterministic_fit_ceiling(
    score: float,
    forward: float,
    reverse: float | None,
    evidence: list[str],
    reciprocal_complete: bool,
) -> FitLevel | None:
    """Highest label the evidence can earn before the LLM may downgrade it."""
    if not reciprocal_complete or reverse is None:
        return None
    directions, categories = _evidence_dimensions(evidence)
    has_both_person_directions = {
        "USER WANTS -> CANDIDATE IS",
        "CANDIDATE WANTS -> USER IS",
    }.issubset(directions)
    if (
        score < WORTH_EXPLORING_THRESHOLD
        or forward < MIN_WORTH_DIRECTION_SCORE
        or reverse < MIN_WORTH_DIRECTION_SCORE
        or len(evidence) < MIN_WORTH_EVIDENCE
        or len(categories) < 2
        or not has_both_person_directions
    ):
        return None
    if (
        score >= STRONG_FIT_THRESHOLD
        and forward >= MIN_RECIPROCAL_DIRECTION_SCORE
        and reverse >= MIN_RECIPROCAL_DIRECTION_SCORE
        and len(evidence) >= MIN_STRONG_EVIDENCE
        and len(categories) >= 3
    ):
        return FitLevel.strong_fit
    return FitLevel.worth_exploring


def find_matches(
    db: Session,
    user_narrative: str,
    user_ideal_partner_signals: list[BlueprintSignal],
    user_me_signals: list[BlueprintSignal] | None = None,
    user_us_signals: list[BlueprintSignal] | None = None,
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    user_gender: str | None = None,
    user_age: int | None = None,
    user_id: str | None = None,
) -> list[MatchOut]:
    """Return at most one introduction after reciprocal eligibility + reasoning."""
    if not user_ideal_partner_signals:
        return []
    user_me_signals = user_me_signals or []
    user_us_signals = user_us_signals or []

    # Direction 1 demographic eligibility: does the candidate satisfy what
    # this user explicitly said they are open to meeting?
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

    # Direction 2 demographic eligibility: is this user inside the candidate's
    # own explicit gender/age preferences? Old seeded candidates without this
    # metadata remain eligible until the pool is reseeded.
    retrieved = [
        (candidate, similarity)
        for candidate, similarity in retrieved
        if _candidate_available_for_user(candidate, user_id)
        and candidate_accepts_user(candidate, user_gender, user_age)
    ]

    # Reciprocal semantic evidence narrows the pool before the expensive
    # relationship reasoner sees anything.
    finalists = semantic_rerank_candidates(
        retrieved,
        user_ideal_partner_signals,
        user_me_signals=user_me_signals,
        user_us_signals=user_us_signals,
        finalist_size=FINALIST_SIZE,
    )

    user_context = (
        "USER IDEAL_PARTNER:\n" + _profile_embedding_text(user_ideal_partner_signals)
        + "\n\nUSER ME:\n" + _profile_embedding_text(user_me_signals)
        + "\n\nUSER US:\n" + _profile_embedding_text(user_us_signals)
    )
    user_hard_requirements = [
        f"{signal.category}: {signal.label}"
        for signal in user_ideal_partner_signals + user_us_signals
        if signal.strength == "hard_requirement"
        and (signal.confidence is None or signal.confidence >= 0.70)
    ]

    has_targeted_demo_fixture = settings.anaphora_demo_mode and any(
        _demo_fixture_marker(candidate, user_id) is not None
        for candidate, *_rest in finalists
    )
    try:
        verdicts = assess_relationship_candidates(
            user_context,
            [
                (candidate, evidence, reciprocal_complete)
                for candidate, _score, _forward, _reverse, evidence, reciprocal_complete in finalists
            ],
            user_hard_requirements=user_hard_requirements,
        )
    except Exception:
        if not has_targeted_demo_fixture:
            raise
        logger.exception(
            "Relationship reasoner failed; eligible targeted demo fixture may use its grounded fallback"
        )
        verdicts = {}

    genuine = []
    for candidate, score, forward, reverse, evidence, reciprocal_complete in finalists:
        has_match, model_fit, sections = verdicts.get(candidate.id, (False, None, []))
        fit_ceiling = deterministic_fit_ceiling(
            score, forward, reverse, evidence, reciprocal_complete
        )
        demo_verdict = _demo_fallback_verdict(candidate, user_id, fit_ceiling)
        if demo_verdict is not None and (not has_match or not sections):
            has_match, model_fit, sections = demo_verdict
            logger.warning("Using grounded demo fallback for candidate=%s", candidate.id)
        if not has_match or not sections or fit_ceiling is None:
            logger.info(
                "match_rejected candidate=%s score=%.3f forward=%.3f reverse=%s evidence=%d model_match=%s ceiling=%s",
                candidate.id, score, forward,
                f"{reverse:.3f}" if reverse is not None else "none",
                len(evidence), has_match, fit_ceiling,
            )
            continue
        fit = (
            FitLevel.strong_fit
            if model_fit == FitLevel.strong_fit and fit_ceiling == FitLevel.strong_fit
            else FitLevel.worth_exploring
        )
        logger.info(
            "match_accepted candidate=%s fit=%s score=%.3f forward=%.3f reverse=%.3f evidence=%d model_fit=%s",
            candidate.id, fit.value, score, forward, reverse, len(evidence), model_fit,
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


def debug_find_matches(
    db: Session,
    user_ideal_partner_signals: list[BlueprintSignal],
    user_me_signals: list[BlueprintSignal] | None = None,
    user_us_signals: list[BlueprintSignal] | None = None,
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    user_gender: str | None = None,
    user_age: int | None = None,
    user_id: str | None = None,
) -> dict:
    """Same pipeline as find_matches, but reports WHERE candidates fall out
    at each stage instead of only the final result — for the admin tester
    tool, so a "no matches" report can be diagnosed from real numbers
    (pool size, eligibility, reranking scores) instead of guessing whether
    the candidate pool needs regenerating or is just too narrow for this
    member's stated preferences. Skips the relationship-reasoning LLM call
    (the final, most expensive gate) since the deterministic stages below
    already show whether anything would even reach it.
    """
    from ..models import Candidate

    pool_total = db.query(Candidate).count()
    user_me_signals = user_me_signals or []
    user_us_signals = user_us_signals or []

    if not user_ideal_partner_signals:
        return {
            "candidate_pool_total": pool_total,
            "error": "No IDEAL_PARTNER signals on this Blueprint — matching never runs without them.",
        }

    query_text = _profile_embedding_text(user_ideal_partner_signals)
    query_embedding = embed_text(query_text)
    retrieved = retrieve_candidates(
        db, query_embedding, k=BROAD_RETRIEVAL_SIZE,
        gender_preference=gender_preference, age_min=age_min, age_max=age_max,
    )
    after_direction1 = len(retrieved)

    retrieved = [
        (candidate, similarity) for candidate, similarity in retrieved
        if _candidate_available_for_user(candidate, user_id)
        and candidate_accepts_user(candidate, user_gender, user_age)
    ]
    after_direction2 = len(retrieved)

    finalists = semantic_rerank_candidates(
        retrieved, user_ideal_partner_signals,
        user_me_signals=user_me_signals, user_us_signals=user_us_signals,
        finalist_size=FINALIST_SIZE,
    )

    finalist_rows = []
    passed_ceiling = 0
    for candidate, score, forward, reverse, evidence, reciprocal_complete in finalists:
        ceiling = deterministic_fit_ceiling(score, forward, reverse, evidence, reciprocal_complete)
        if ceiling is not None:
            passed_ceiling += 1
        finalist_rows.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "score": round(score, 3),
            "forward": round(forward, 3),
            "reverse": round(reverse, 3) if reverse is not None else None,
            "evidence_count": len(evidence),
            "reciprocal_complete": reciprocal_complete,
            "would_pass_deterministic_gate": ceiling.value if ceiling else None,
        })

    return {
        "candidate_pool_total": pool_total,
        "user_signal_counts": {
            "ideal_partner": len(user_ideal_partner_signals),
            "me": len(user_me_signals),
            "us": len(user_us_signals),
        },
        "after_direction1_demographic_filter": after_direction1,
        "after_direction2_reverse_eligibility": after_direction2,
        "finalists_after_reranking": finalist_rows,
        "finalists_that_would_reach_relationship_reasoning": passed_ceiling,
        "thresholds": {
            "worth_exploring_score": WORTH_EXPLORING_THRESHOLD,
            "strong_fit_score": STRONG_FIT_THRESHOLD,
            "min_worth_direction_score": MIN_WORTH_DIRECTION_SCORE,
            "min_reciprocal_direction_score": MIN_RECIPROCAL_DIRECTION_SCORE,
            "min_worth_evidence": MIN_WORTH_EVIDENCE,
            "min_strong_evidence": MIN_STRONG_EVIDENCE,
        },
    }
