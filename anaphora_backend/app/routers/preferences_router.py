from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..readiness import compute_readiness

router = APIRouter(prefix="/preferences", tags=["preferences"])

ALLOWED_GENDERS = {"woman", "man", "nonbinary", "other"}
ALLOWED_PREFERENCES = {"women", "men", "nonbinary", "other", "everyone"}


def _split_other(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    if value.startswith("other:"):
        return "other", value.split(":", 1)[1] or None
    return value, None


def _encode_gender(gender: str, detail: str | None) -> str:
    if gender == "other":
        clean = (detail or "").strip()
        if not clean:
            raise HTTPException(400, "Tell us more about your gender")
        return f"other:{clean}"
    return gender


def _decode_preferences(value: str | None) -> tuple[list[str], str | None]:
    if not value:
        return [], None
    result: list[str] = []
    detail = None
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if token.startswith("other:"):
            result.append("other")
            detail = token.split(":", 1)[1] or None
        else:
            result.append(token)
    return result, detail


def _encode_preferences(values: list[str], detail: str | None) -> str:
    cleaned = list(dict.fromkeys(v.strip().lower() for v in values if v and v.strip()))
    invalid = [v for v in cleaned if v not in ALLOWED_PREFERENCES]
    if invalid:
        raise HTTPException(400, f"Unsupported preference: {invalid[0]}")
    if not cleaned:
        raise HTTPException(400, "Choose at least one gender preference")
    if "everyone" in cleaned:
        return "everyone"
    if "other" in cleaned:
        other_detail = (detail or "").strip()
        if not other_detail:
            raise HTTPException(400, "Tell us more about who else you're open to meeting")
        cleaned = [f"other:{other_detail}" if v == "other" else v for v in cleaned]
    return ",".join(cleaned)


def _age_on(birth_date: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


class MatchingPreferencesUpdate(BaseModel):
    # Both cards can be saved independently.
    user_gender: str | None = None
    user_gender_detail: str | None = Field(default=None, max_length=80)
    birth_date: date | None = None
    gender_preferences: list[str] | None = None
    gender_preference_detail: str | None = Field(default=None, max_length=80)

    # Legacy fields retained during deployment overlap.
    user_age: int | None = Field(default=None, ge=18, le=99)
    gender_preference: str | None = Field(default=None, min_length=1)
    age_min: int | None = Field(default=None, ge=18, le=99)
    age_max: int | None = Field(default=None, ge=18, le=99)


class MatchingPreferencesOut(BaseModel):
    user_gender: str | None
    user_gender_detail: str | None
    birth_date: date | None
    user_age: int | None
    gender_preferences: list[str]
    gender_preference_detail: str | None
    age_min: int | None
    age_max: int | None
    gender_preference: str | None


class MatchingPreferencesResponse(MatchingPreferencesOut):
    readiness_pct: int
    readiness_breakdown: dict[str, dict]


def _response_values(user: User) -> dict:
    age_min = age_max = None
    if user.preferred_age_range:
        try:
            low, high = user.preferred_age_range.split("-", 1)
            age_min, age_max = int(low), int(high)
        except (ValueError, TypeError):
            pass
    user_gender, user_gender_detail = _split_other(user.gender)
    gender_preferences, gender_preference_detail = _decode_preferences(user.gender_preference)
    derived_age = _age_on(user.birth_date) if user.birth_date else user.age
    return {
        "user_gender": user_gender,
        "user_gender_detail": user_gender_detail,
        "birth_date": user.birth_date,
        "user_age": derived_age,
        "gender_preferences": gender_preferences,
        "gender_preference_detail": gender_preference_detail,
        "age_min": age_min,
        "age_max": age_max,
        "gender_preference": user.gender_preference,
    }


@router.get("", response_model=MatchingPreferencesOut)
def get_matching_preferences(user: User = Depends(get_current_user)):
    return MatchingPreferencesOut(**_response_values(user))


@router.patch("", response_model=MatchingPreferencesResponse)
def save_matching_preferences(
    body: MatchingPreferencesUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.user_gender is not None:
        gender = body.user_gender.strip().lower()
        if gender not in ALLOWED_GENDERS:
            raise HTTPException(400, "Unsupported gender")
        user.gender = _encode_gender(gender, body.user_gender_detail)

    if body.birth_date is not None:
        derived_age = _age_on(body.birth_date)
        if derived_age < 18:
            raise HTTPException(400, "You must be at least 18")
        if derived_age > 99:
            raise HTTPException(400, "Please enter a valid birth date")
        user.birth_date = body.birth_date
        user.age = derived_age
    elif body.user_age is not None:
        # Backwards-compatible only; new UI sends birth_date.
        user.age = body.user_age

    preference_values = body.gender_preferences
    if preference_values is None and body.gender_preference is not None:
        legacy = body.gender_preference.strip().lower()
        preference_values = {
            "women": ["women"], "woman": ["women"], "female": ["women"],
            "men": ["men"], "man": ["men"], "male": ["men"],
            "non-binary": ["nonbinary"], "nonbinary": ["nonbinary"],
            "everyone": ["everyone"], "all": ["everyone"], "any": ["everyone"],
        }.get(legacy, [legacy])
    if preference_values is not None:
        user.gender_preference = _encode_preferences(preference_values, body.gender_preference_detail)

    if (body.age_min is None) != (body.age_max is None):
        raise HTTPException(400, "Set both minimum and maximum age")
    if body.age_min is not None and body.age_max is not None:
        if body.age_min > body.age_max:
            raise HTTPException(400, "Minimum age cannot be greater than maximum age")
        user.preferred_age_range = f"{body.age_min}-{body.age_max}"

    db.add(user)
    db.commit()
    db.refresh(user)

    readiness_pct, breakdown = compute_readiness(db, user.id)
    return MatchingPreferencesResponse(
        **_response_values(user),
        readiness_pct=readiness_pct,
        readiness_breakdown=breakdown,
    )
