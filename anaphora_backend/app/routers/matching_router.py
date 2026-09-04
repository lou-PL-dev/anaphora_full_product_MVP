from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..chains.matching_chain_v5 import find_matches
from ..database import engine, get_db
from ..models import BlueprintSignal, User
from ..readiness import compute_readiness
from ..schemas import MatchListResponse

router = APIRouter(prefix="/matches", tags=["matches"])


def _preferred_age_bounds(value: str | None) -> tuple[int | None, int | None]:
    if not value:
        return None, None
    try:
        low, high = value.split("-", 1)
        return int(low), int(high)
    except (ValueError, TypeError):
        return None, None


@router.get("", response_model=MatchListResponse)
def get_matches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if engine.dialect.name != "postgresql":
        raise HTTPException(503, "Matching requires Postgres with pgvector — not available on local SQLite dev")

    readiness_pct, _breakdown = compute_readiness(db, user.id)
    if readiness_pct < 100:
        return MatchListResponse(ready=False, readiness_pct=readiness_pct, matches=[])

    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
    ideal_partner_signals = [s for s in signals if s.perspective == "IDEAL_PARTNER"]
    me_signals = [s for s in signals if s.perspective == "ME"]
    us_signals = [s for s in signals if s.perspective == "US"]

    age_min, age_max = _preferred_age_bounds(user.preferred_age_range)
    matches = find_matches(
        db,
        user.blueprint_narrative or "",
        ideal_partner_signals,
        user_me_signals=me_signals,
        user_us_signals=us_signals,
        gender_preference=user.gender_preference,
        age_min=age_min,
        age_max=age_max,
        user_gender=user.gender,
        user_age=user.age,
        user_id=user.id,
    )
    return MatchListResponse(ready=True, readiness_pct=readiness_pct, matches=matches)
