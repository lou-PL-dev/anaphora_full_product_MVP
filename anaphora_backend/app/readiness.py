"""Deterministic matching readiness.

Readiness answers one narrow question: do we know enough to start making
responsible introductions? It is not a measure of how rich or complete the
Relationship Blueprint is. Once readiness reaches 100%, later conversations,
Discoveries and friend input can keep deepening the Blueprint without changing
this score.

Four independent gates:
- 20% basic matching preferences
- 20% at least one completed Discovery
- 30% sufficient ME coverage
- 30% sufficient IDEAL_PARTNER coverage

ME and IDEAL_PARTNER use the same core dimensions. A side is sufficiently
covered when personality, lifestyle and relationship_dynamic are present, plus
at least two additional core dimensions. This avoids turning onboarding into a
rigid 7/7 questionnaire while still requiring a meaningful profile.
"""
from sqlalchemy.orm import Session

from .models import BlueprintSignal, DiscoveryResponse, User

CORE_CATEGORIES = {
    "personality",
    "lifestyle",
    "physical_type",
    "relationship_dynamic",
    "love_language",
    "dealbreakers",
    "values",
}
MANDATORY_CATEGORIES = {
    "personality",
    "lifestyle",
    "relationship_dynamic",
}
MIN_CATEGORIES_PER_SIDE = 5

CATEGORY_WEIGHTS = {
    "basic_matching_preferences": 20,
    "discovery_completed": 20,
    "me_profile": 30,
    "ideal_partner_profile": 30,
}


def _coverage(signals: list[BlueprintSignal], perspective: str) -> set[str]:
    return {
        signal.category
        for signal in signals
        if signal.perspective == perspective and signal.category in CORE_CATEGORIES
    }


def category_coverage(signals: list[BlueprintSignal]) -> tuple[set[str], set[str]]:
    """(me_covered, ideal_partner_covered) from every signal source (conversation
    + Discovery). Conversation steering uses this so a follow-up conversation
    knows what's already established instead of judging depth from its own
    empty transcript alone."""
    return _coverage(signals, "ME"), _coverage(signals, "IDEAL_PARTNER")


def _profile_ready(covered: set[str]) -> bool:
    return (
        MANDATORY_CATEGORIES.issubset(covered)
        and len(covered) >= MIN_CATEGORIES_PER_SIDE
    )


def compute_readiness(db: Session, user_id: str) -> tuple[int, dict]:
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user_id).all()
    user = db.get(User, user_id)
    has_discovery = (
        db.query(DiscoveryResponse)
        .filter(DiscoveryResponse.user_id == user_id)
        .first()
        is not None
    )

    me_covered = _coverage(signals, "ME")
    ideal_partner_covered = _coverage(signals, "IDEAL_PARTNER")

    checks = {
        "basic_matching_preferences": bool(
            user and user.gender_preference and user.preferred_age_range
        ),
        "discovery_completed": has_discovery,
        "me_profile": _profile_ready(me_covered),
        "ideal_partner_profile": _profile_ready(ideal_partner_covered),
    }

    breakdown = {
        "basic_matching_preferences": {
            "weight": CATEGORY_WEIGHTS["basic_matching_preferences"],
            "met": checks["basic_matching_preferences"],
        },
        "discovery_completed": {
            "weight": CATEGORY_WEIGHTS["discovery_completed"],
            "met": checks["discovery_completed"],
        },
        "me_profile": {
            "weight": CATEGORY_WEIGHTS["me_profile"],
            "met": checks["me_profile"],
            "covered_categories": sorted(me_covered),
        },
        "ideal_partner_profile": {
            "weight": CATEGORY_WEIGHTS["ideal_partner_profile"],
            "met": checks["ideal_partner_profile"],
            "covered_categories": sorted(ideal_partner_covered),
        },
    }

    total = sum(
        CATEGORY_WEIGHTS[key]
        for key, met in checks.items()
        if met
    )
    return total, breakdown
