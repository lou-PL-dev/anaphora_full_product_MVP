from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..readiness import compute_readiness

router = APIRouter(prefix="/profile", tags=["profile"])


class MatchingPreferencesIn(BaseModel):
    gender_preference: str
    preferred_age_range: str


@router.patch("/matching-preferences")
def update_matching_preferences(
    body: MatchingPreferencesIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Persist the minimum eligibility preferences used by readiness.

    This intentionally stays separate from the Relationship Blueprint:
    eligibility (who/age) is a hard matching filter, while Blueprint signals
    describe reciprocal fit.
    """
    user.gender_preference = body.gender_preference
    user.preferred_age_range = body.preferred_age_range
    db.add(user)
    db.commit()
    db.refresh(user)

    readiness_pct, breakdown = compute_readiness(db, user.id)
    return {
        "gender_preference": user.gender_preference,
        "preferred_age_range": user.preferred_age_range,
        "readiness_pct": readiness_pct,
        "breakdown": breakdown,
    }
