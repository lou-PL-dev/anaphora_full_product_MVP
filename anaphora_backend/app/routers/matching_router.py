from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..chains.matching_chain import find_matches
from ..database import engine, get_db
from ..models import BlueprintSignal, User
from ..readiness import compute_readiness
from ..schemas import MatchListResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchListResponse)
def get_matches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if engine.dialect.name != "postgresql":
        raise HTTPException(503, "Matching requires Postgres with pgvector — not available on local SQLite dev")

    readiness_pct, _breakdown = compute_readiness(db, user.id)
    if readiness_pct < 100:
        # Not an error — a normal, expected state. The frontend uses `ready`
        # to redirect back to the conversation rather than showing an empty
        # Matches screen or a fake error.
        return MatchListResponse(ready=False, readiness_pct=readiness_pct, matches=[])

    ideal_partner_signals = (
        db.query(BlueprintSignal)
        .filter(BlueprintSignal.user_id == user.id, BlueprintSignal.perspective == "IDEAL_PARTNER")
        .all()
    )
    matches = find_matches(db, user.blueprint_narrative or "", ideal_partner_signals)
    return MatchListResponse(ready=True, readiness_pct=readiness_pct, matches=matches)
