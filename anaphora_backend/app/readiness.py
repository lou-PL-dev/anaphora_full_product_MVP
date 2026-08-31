"""Matching readiness: minimum viable information required for introductions.

Readiness is deliberately NOT a measure of how rich the Relationship Blueprint
is. It reaches 100% once Anaphora has enough information to match responsibly;
the Blueprint can continue deepening forever through conversation, Discoveries
and (later) friend perspectives.

Four independent gates:
- 20% basic matching preferences
- 20% at least one completed Discovery
- 30% enough information about ME
- 30% enough information about IDEAL_PARTNER

ME and IDEAL_PARTNER are symmetric. Both use the same seven core categories.
For either perspective to be ready we require the three most important matching
anchors plus at least five distinct core categories overall. This keeps the
conversation natural rather than forcing users through a rigid 7/7 checklist.
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
MANDATORY_CORE_CATEGORIES = {"personality", "lifestyle", "relationship_dynamic"}
MIN_CORE_CATEGORIES = 5

READINESS_WEIGHTS = {
    "basic_matching_preferences": 20,
    "discovery_completed": 20,
    "me_profile": 30,
    "ideal_partner_profile": 30,
}


def _perspective_coverage(signals: list[BlueprintSignal], perspective: str) -> tuple[bool, list[str]]:
    """Return readiness + sorted covered categories for one Blueprint side."""
    covered = {
        s.category
        for s in signals
        if s.perspective == perspective and s.category in CORE_CATEGORIES
    }
    ready = MANDATORY_CORE_CATEGORIES.issubset(covered) and len(covered) >= MIN_CORE_CATEGORIES
    return ready, sorted(covered)


def compute_readiness(db: Session, user_id: str) -> tuple[int, dict]:
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user_id).all()
    user = db.get(User, user_id)

    # One or more saved responses are enough to establish that at least one
    # Discovery was completed. Additional Discoveries deepen the Blueprint but
    # never add more readiness points.
    has_discovery = (
        db.query(DiscoveryResponse)
        .filter(DiscoveryResponse.user_id == user_id)
        .first()
        is not None
    )

    me_ready, me_covered = _perspective_coverage(signals, "ME")
    ideal_ready, ideal_covered = _perspective_coverage(signals, "IDEAL_PARTNER")
    prefs_ready = bool(user and user.gender_preference and user.preferred_age_range)

    checks = {
        "basic_matching_preferences": prefs_ready,
        "discovery_completed": has_discovery,
        "me_profile": me_ready,
        "ideal_partner_profile": ideal_ready,
    }

    breakdown = {
        key: {
            "weight": READINESS_WEIGHTS[key],
            "met": met,
            **(
                {
                    "covered_categories": me_covered,
                    "required_categories": sorted(MANDATORY_CORE_CATEGORIES),
                    "minimum_categories": MIN_CORE_CATEGORIES,
                }
                if key == "me_profile"
                else {}
            ),
            **(
                {
                    "covered_categories": ideal_covered,
                    "required_categories": sorted(MANDATORY_CORE_CATEGORIES),
                    "minimum_categories": MIN_CORE_CATEGORIES,
                }
                if key == "ideal_partner_profile"
                else {}
            ),
        }
        for key, met in checks.items()
    }

    total = sum(READINESS_WEIGHTS[key] for key, met in checks.items() if met)
    return total, breakdown
