"""Deterministic introduction readiness.

Readiness answers one narrow question: do we know enough to start making
responsible introductions? It is not a measure of how rich or complete the
Relationship Blueprint is. Once readiness reaches 100%, later conversations,
Discoveries and friend input can keep deepening the Blueprint without changing
this score.

Four product-facing areas:
- 20% introduction essentials (10% your essentials + 10% who you'd like to meet)
- 20% at least one completed Discovery
- 30% sufficient ME coverage
- 30% sufficient IDEAL_PARTNER coverage

The introduction-essentials row is only marked complete when both halves are
complete, while each half still contributes 10% to the numeric readiness.
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
    "introduction_essentials": 20,
    "discovery_completed": 20,
    "me_profile": 30,
    "ideal_partner_profile": 30,
}
INTRODUCTION_ESSENTIALS_PART_WEIGHT = 10


def _coverage(signals: list[BlueprintSignal], perspective: str) -> set[str]:
    return {
        signal.category
        for signal in signals
        if signal.perspective == perspective and signal.category in CORE_CATEGORIES
    }


def category_coverage(signals: list[BlueprintSignal]) -> tuple[set[str], set[str]]:
    """(me_covered, ideal_partner_covered) from every signal source."""
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

    your_essentials_met = bool(user and user.gender and user.birth_date)
    meeting_preferences_met = bool(
        user and user.gender_preference and user.preferred_age_range
    )
    introduction_essentials_met = your_essentials_met and meeting_preferences_met

    discovery_met = bool(has_discovery)
    me_profile_met = _profile_ready(me_covered)
    ideal_partner_profile_met = _profile_ready(ideal_partner_covered)

    introduction_essentials_score = (
        (INTRODUCTION_ESSENTIALS_PART_WEIGHT if your_essentials_met else 0)
        + (INTRODUCTION_ESSENTIALS_PART_WEIGHT if meeting_preferences_met else 0)
    )

    total = (
        introduction_essentials_score
        + (CATEGORY_WEIGHTS["discovery_completed"] if discovery_met else 0)
        + (CATEGORY_WEIGHTS["me_profile"] if me_profile_met else 0)
        + (CATEGORY_WEIGHTS["ideal_partner_profile"] if ideal_partner_profile_met else 0)
    )

    breakdown = {
        "introduction_essentials": {
            "weight": CATEGORY_WEIGHTS["introduction_essentials"],
            "earned": introduction_essentials_score,
            "met": introduction_essentials_met,
            "parts": {
                "your_essentials": {
                    "weight": INTRODUCTION_ESSENTIALS_PART_WEIGHT,
                    "met": your_essentials_met,
                },
                "meeting_preferences": {
                    "weight": INTRODUCTION_ESSENTIALS_PART_WEIGHT,
                    "met": meeting_preferences_met,
                },
            },
        },
        "discovery_completed": {
            "weight": CATEGORY_WEIGHTS["discovery_completed"],
            "earned": CATEGORY_WEIGHTS["discovery_completed"] if discovery_met else 0,
            "met": discovery_met,
        },
        "me_profile": {
            "weight": CATEGORY_WEIGHTS["me_profile"],
            "earned": CATEGORY_WEIGHTS["me_profile"] if me_profile_met else 0,
            "met": me_profile_met,
            "covered_categories": sorted(me_covered),
        },
        "ideal_partner_profile": {
            "weight": CATEGORY_WEIGHTS["ideal_partner_profile"],
            "earned": CATEGORY_WEIGHTS["ideal_partner_profile"] if ideal_partner_profile_met else 0,
            "met": ideal_partner_profile_met,
            "covered_categories": sorted(ideal_partner_covered),
        },
    }

    return total, breakdown
