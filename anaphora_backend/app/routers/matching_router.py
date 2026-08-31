from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..chains.matching_chain import find_matches
from ..database import engine, get_db
from ..models import BlueprintSignal, User
from ..schemas import MatchListResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchListResponse)
def get_matches(k: int = 5, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if engine.dialect.name != "postgresql":
        raise HTTPException(503, "Matching requires Postgres with pgvector — not available on local SQLite dev")

    if not user.blueprint_narrative:
        raise HTTPException(400, "Complete a conversation first — matching needs an ideal_partner Blueprint")

    ideal_partner_signals = (
        db.query(BlueprintSignal)
        .filter(BlueprintSignal.user_id == user.id, BlueprintSignal.perspective == "IDEAL_PARTNER")
        .all()
    )
    matches = find_matches(db, user.blueprint_narrative, ideal_partner_signals, k=k)
    return MatchListResponse(matches=matches)
