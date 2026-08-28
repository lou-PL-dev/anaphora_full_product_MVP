from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, BlueprintSignal
from ..schemas import BlueprintSignalOut, SignalCorrectionRequest

router = APIRouter(prefix="/blueprint", tags=["blueprint"])


@router.get("", response_model=list[BlueprintSignalOut])
def get_blueprint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
    return [BlueprintSignalOut.model_validate(s) for s in signals]


@router.patch("/signal/{signal_id}", response_model=BlueprintSignalOut)
def correct_signal(
    signal_id: str,
    body: SignalCorrectionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """PRD section 14: 'Change something' — simple correction, not a full
    conversational re-negotiation, is sufficient for MVP."""
    signal = db.get(BlueprintSignal, signal_id)
    if not signal or signal.user_id != user.id:
        raise HTTPException(404, "Signal not found")
    if body.label is not None:
        signal.label = body.label
    if body.strength is not None:
        signal.strength = body.strength.value
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return BlueprintSignalOut.model_validate(signal)
