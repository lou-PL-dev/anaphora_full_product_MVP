from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..readiness import compute_readiness

router = APIRouter(prefix="/preferences", tags=["preferences"])


class MatchingPreferencesUpdate(BaseModel):
    gender_preference: str = Field(min_length=1)
    age_min: int = Field(ge=18, le=99)
    age_max: int = Field(ge=18, le=99)


class MatchingPreferencesResponse(BaseModel):
    gender_preference: str
    age_min: int
    age_max: int
    readiness_pct: int


class MatchingPreferencesOut(BaseModel):
    gender_preference: str | None
    age_min: int | None
    age_max: int | None


@router.get("", response_model=MatchingPreferencesOut)
def get_matching_preferences(user: User = Depends(get_current_user)):
    age_min = age_max = None
    if user.preferred_age_range:
        try:
            low, high = user.preferred_age_range.split("-", 1)
            age_min, age_max = int(low), int(high)
        except (ValueError, TypeError):
            pass
    return MatchingPreferencesOut(
        gender_preference=user.gender_preference,
        age_min=age_min,
        age_max=age_max,
    )


@router.patch("", response_model=MatchingPreferencesResponse)
def save_matching_preferences(
    body: MatchingPreferencesUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.age_min > body.age_max:
        raise HTTPException(400, "Minimum age cannot be greater than maximum age")

    user.gender_preference = body.gender_preference
    user.preferred_age_range = f"{body.age_min}-{body.age_max}"
    db.add(user)
    db.commit()
    db.refresh(user)

    readiness_pct, _ = compute_readiness(db, user.id)
    return MatchingPreferencesResponse(
        gender_preference=user.gender_preference,
        age_min=body.age_min,
        age_max=body.age_max,
        readiness_pct=readiness_pct,
    )
