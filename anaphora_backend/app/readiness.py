"""Deterministic introduction readiness for the ME / YOU / US Blueprint.

US signals deepen the Blueprint and matching, but they are optional enrichment
and never block an introduction. The four readiness areas are essentials,
one Discovery, sufficient ME coverage, and sufficient IDEAL_PARTNER coverage.
"""
from sqlalchemy.orm import Session

from .models import BlueprintSignal, DiscoveryResponse, User

ALLOWED = {
    "ME": {"personality", "lifestyle", "relationship_behavior", "core_values"},
    "IDEAL_PARTNER": {"personality", "lifestyle", "physical_type"},
    "US": {"relationship_shape", "connection_affection", "shared_direction", "boundaries"},
}
CATEGORY_WEIGHTS = {
    "introduction_essentials": 20,
    "discovery_completed": 20,
    "me_profile": 30,
    "ideal_partner_profile": 30,
}


def _coverage(signals, perspective):
    return {
        signal.category for signal in signals
        if signal.perspective == perspective and signal.category in ALLOWED[perspective]
    }


def category_coverage(signals):
    return _coverage(signals, "ME"), _coverage(signals, "IDEAL_PARTNER"), _coverage(signals, "US")


def _me_ready(covered):
    return {"personality", "lifestyle"}.issubset(covered) and len(covered) >= 3


def _ideal_ready(covered):
    # Physical attraction is deliberately part of a useful YOU profile; "no
    # fixed type" is itself valid evidence and can cover physical_type.
    return ALLOWED["IDEAL_PARTNER"].issubset(covered)


def compute_readiness(db: Session, user_id: str) -> tuple[int, dict]:
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user_id).all()
    user = db.get(User, user_id)
    has_discovery = db.query(DiscoveryResponse).filter(DiscoveryResponse.user_id == user_id).first() is not None
    me, ideal, _us = category_coverage(signals)

    your_essentials_met = bool(user and user.gender and user.birth_date)
    meeting_preferences_met = bool(user and user.gender_preference and user.preferred_age_range)
    introduction_score = (10 if your_essentials_met else 0) + (10 if meeting_preferences_met else 0)
    statuses = {
        "discovery_completed": bool(has_discovery),
        "me_profile": _me_ready(me),
        "ideal_partner_profile": _ideal_ready(ideal),
    }
    total = introduction_score + sum(CATEGORY_WEIGHTS[key] for key, met in statuses.items() if met)
    breakdown = {
        "introduction_essentials": {
            "weight": 20, "earned": introduction_score,
            "met": your_essentials_met and meeting_preferences_met,
            "parts": {
                "your_essentials": {"weight": 10, "met": your_essentials_met},
                "meeting_preferences": {"weight": 10, "met": meeting_preferences_met},
            },
        },
        "discovery_completed": {"weight": 20, "earned": 20 if statuses["discovery_completed"] else 0, "met": statuses["discovery_completed"]},
        "me_profile": {"weight": 30, "earned": 30 if statuses["me_profile"] else 0, "met": statuses["me_profile"], "covered_categories": sorted(me)},
        "ideal_partner_profile": {"weight": 30, "earned": 30 if statuses["ideal_partner_profile"] else 0, "met": statuses["ideal_partner_profile"], "covered_categories": sorted(ideal)},
    }
    return total, breakdown
