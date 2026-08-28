"""
Readiness (PRD section 17) — deterministic information-coverage %, not a
match-quality score. Each category is worth its weight in full once at
least one qualifying signal/response exists for it.
"""
from sqlalchemy.orm import Session

from .models import BlueprintSignal, DiscoveryResponse, User

CATEGORY_WEIGHTS = {
    "ideal_partner_personality": 15,
    "ideal_partner_lifestyle": 15,
    "relationship_needs": 15,       # ideal_partner.relationship_dynamic
    "attraction": 10,               # ideal_partner.attraction
    "about_me": 15,                 # any ME-perspective signal
    "values": 10,                   # ideal_partner.values OR me.values
    "discovery_completed": 10,      # any discovery_responses row
    "basic_matching_preferences": 10,  # user.gender_preference + preferred_age_range set
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
        "relationship_needs": has_signal("IDEAL_PARTNER", "relationship_dynamic"),
        "attraction": has_signal("IDEAL_PARTNER", "attraction"),
        "about_me": has_signal("ME"),
        "values": has_signal("IDEAL_PARTNER", "values") or has_signal("ME", "values"),
        "discovery_completed": has_discovery,
        "basic_matching_preferences": bool(user and user.gender_preference and user.preferred_age_range),
    }

    breakdown = {
        key: {"weight": CATEGORY_WEIGHTS[key], "met": met}
        for key, met in checks.items()
    }
    total = sum(CATEGORY_WEIGHTS[key] for key, met in checks.items() if met)
    return total, breakdown
