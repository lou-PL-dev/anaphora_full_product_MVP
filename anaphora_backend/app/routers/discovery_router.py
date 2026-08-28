from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, DiscoveryResponse, BlueprintSignal
from ..schemas import DiscoveryResponseIn, DiscoveryResultResponse, BlueprintSignalOut
from ..chains.discovery_chain import DISCOVERY_ID, DISCOVERY_TITLE, QUESTIONS, synthesize_insight, responses_to_signals
from ..readiness import compute_readiness

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("/{discovery_id}")
def get_discovery(discovery_id: str):
    if discovery_id != DISCOVERY_ID:
        raise HTTPException(404, "Discovery not found (MVP only implements one)")
    return {"id": DISCOVERY_ID, "title": DISCOVERY_TITLE, "questions": QUESTIONS}


@router.post("/{discovery_id}/respond", response_model=DiscoveryResultResponse)
def respond_to_discovery(
    discovery_id: str,
    body: list[DiscoveryResponseIn],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if discovery_id != DISCOVERY_ID:
        raise HTTPException(404, "Discovery not found (MVP only implements one)")

    responses_map: dict[str, str] = {}
    for item in body:
        db.add(DiscoveryResponse(
            user_id=user.id, discovery_id=discovery_id,
            question_id=item.question_id, response=item.response,
        ))
        responses_map[item.question_id] = item.response
    db.commit()

    insight_text = synthesize_insight(responses_map)
    new_signal_items = responses_to_signals(responses_map)

    created = []
    for item in new_signal_items:
        signal = BlueprintSignal(
            user_id=user.id, perspective="ME", category="lifestyle",
            label=item.label, strength=item.strength.value,
            source="discovery", evidence_text=item.evidence_text,
        )
        db.add(signal)
        created.append(signal)
    db.commit()
    for s in created:
        db.refresh(s)

    readiness_pct, _ = compute_readiness(db, user.id)

    return DiscoveryResultResponse(
        insight_text=insight_text,
        new_signals=[BlueprintSignalOut.model_validate(s) for s in created],
        readiness_pct=readiness_pct,
    )