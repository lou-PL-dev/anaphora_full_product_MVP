from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, BlueprintSignal
from ..blueprint_canonicalizer import add_evidence, ensure_evidence_backfill, rebuild_blueprint
from ..schemas import BlueprintResponse, BlueprintSignalOut, SignalCorrectionRequest

router = APIRouter(prefix="/blueprint", tags=["blueprint"])


@router.get("", response_model=BlueprintResponse)
def get_blueprint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
    return BlueprintResponse(
        signals=[BlueprintSignalOut.model_validate(s) for s in signals],
        narrative=user.blueprint_narrative,
    )


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
    new_label = body.label.strip() if body.label is not None else signal.label
    if not new_label:
        raise HTTPException(400, "Signal label cannot be empty")
    new_strength = body.strength.value if body.strength is not None else signal.strength

    try:
        ensure_evidence_backfill(db, user.id)
        linked_ids = list(signal.evidence_ids or [signal.id])
        correction = add_evidence(
            db,
            user_id=user.id,
            perspective=signal.perspective,
            category=signal.category,
            label=new_label,
            strength=new_strength,
            source=f"user_correction:{signal.id}",
            evidence_text=None,
            confidence=1.0,
            explicit=True,
        )
        correction.supersedes_evidence_ids = linked_ids
        db.add(correction)
        canonical_signals = rebuild_blueprint(db, user)
        corrected = next(
            (item for item in canonical_signals if correction.id in (item.evidence_ids or [])),
            None,
        )
        if corrected is None:
            raise ValueError("Member correction was omitted from the canonical Blueprint")
        db.commit()
        return BlueprintSignalOut.model_validate(corrected)
    except Exception:
        db.rollback()
        raise
