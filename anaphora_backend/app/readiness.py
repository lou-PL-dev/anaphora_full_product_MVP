"""
Readiness (PRD section 17) — deterministic information-coverage %, not a
match-quality score. Each category is worth its weight in full once at
least one qualifying signal/response exists for it.

The 7 conversation-based checks below mirror BASE_CATEGORIES in
chains/conversation_chain.py — the same fields the conversation itself is
built to steer toward until they're covered.
"""
from sqlalchemy.orm import Session

from .models import BlueprintSignal, DiscoveryResponse, User

CATEGORY_WEIGHTS = {
    "ideal_partner_personality": 10,
    "ideal_partner_lifestyle": 10,
    "ideal_partner_physical_type": 10,
    "ideal_partner_relationship_dynamic": 10,
    "ideal_partner_love_language": 10,
    "ideal_partner_dealbreakers": 10,
    "about_you": 10,                   # any ME-perspective signal, any category
    "discovery_completed": 15,         # any discovery_responses row
    "basic_matching_preferences": 15,  # user.gender_preference + preferred_age_range set
}


def compute_readiness(db: Session, user_id: str) -> tuple[int, dict]:
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user_id).all()
    user = db.get(User, user_id)
    has_discovery = db.query(DiscoveryResponse).filter(DiscoveryResponse.user_id == user_id).first() is not None

    def has_signal(perspective: str | None, category: str | None = None) -> bool:
        for s in signals:
            if perspective and s.perspective != perspective:
                continue
            if category and s.category != category:
                continue
            return True
        return False

    checks = {
        "ideal_partner_personality": has_signal("IDEAL_PARTNER", "personality"),
        "ideal_partner_lifestyle": has_signal("IDEAL_PARTNER", "lifestyle"),
        "ideal_partner_physical_type": has_signal("IDEAL_PARTNER", "physical_type"),
        "ideal_partner_relationship_dynamic": has_signal("IDEAL_PARTNER", "relationship_dynamic"),
        "ideal_partner_love_language": has_signal("IDEAL_PARTNER", "love_language"),
        "ideal_partner_dealbreakers": has_signal("IDEAL_PARTNER", "dealbreakers"),
        "about_you": has_signal("ME"),
        "discovery_completed": has_discovery,
        "basic_matching_preferences": bool(user and user.gender_preference and user.preferred_age_range),
    }

    breakdown = {
        key: {"weight": CATEGORY_WEIGHTS[key], "met": met}
        for key, met in checks.items()
    }
    total = sum(CATEGORY_WEIGHTS[key] for key, met in checks.items() if met)
    return total, breakdown
