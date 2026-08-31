from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, DiscoveryResponse, BlueprintSignal
from ..schemas import DiscoveryResponseIn, DiscoveryResultResponse, BlueprintSignalOut
from ..discovery_registry import get_discovery_spec
from ..readiness import compute_readiness

router = APIRouter(prefix="/discovery", tags=["discovery"])


def _spec_or_404(discovery_id: str):
    spec = get_discovery_spec(discovery_id)
    if spec is None or spec.status != "active":
        raise HTTPException(404, "Discovery not found")
    return spec


@router.get("/{discovery_id}")
def get_discovery(discovery_id: str):
    spec = _spec_or_404(discovery_id)
    return {"id": spec.id, "title": spec.title, "questions": spec.questions}


@router.post("/{discovery_id}/respond", response_model=DiscoveryResultResponse)
def respond_to_discovery(
    discovery_id: str,
    body: list[DiscoveryResponseIn],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    spec = _spec_or_404(discovery_id)
    if not body:
        raise HTTPException(400, "At least one Discovery response is required")

    valid_question_ids = {q["id"] for q in spec.questions}
    responses_map: dict[str, str] = {}
    for item in body:
        if item.question_id not in valid_question_ids:
            raise HTTPException(400, f"Unknown question for this Discovery: {item.question_id}")
        responses_map[item.question_id] = item.response

    # Generate first, then persist everything together. If the LLM fails,
    # no half-completed Discovery responses are left in the database.
    insight_text = spec.synthesize_insight(responses_map)
    new_signal_items = spec.responses_to_signals(responses_map)

    created = []
    try:
        # Retrying a completed submission replaces this Discovery's previous
        # data instead of duplicating responses/signals. This also makes the
        # frontend's background retry safe.
        db.query(DiscoveryResponse).filter(
            DiscoveryResponse.user_id == user.id,
            DiscoveryResponse.discovery_id == discovery_id,
        ).delete(synchronize_session=False)
        db.query(BlueprintSignal).filter(
            BlueprintSignal.user_id == user.id,
            BlueprintSignal.source == "discovery",
            BlueprintSignal.category == spec.category,
        ).delete(synchronize_session=False)

        for item in body:
            db.add(DiscoveryResponse(
                user_id=user.id,
                discovery_id=discovery_id,
                question_id=item.question_id,
                response=item.response,
            ))

        for item in new_signal_items:
            signal = BlueprintSignal(
                user_id=user.id,
                perspective=spec.perspective,
                category=spec.category,
                label=item.label,
                strength=item.strength.value,
                source="discovery",
                evidence_text=item.evidence_text,
            )
            db.add(signal)
            created.append(signal)

        db.commit()
        for signal in created:
            db.refresh(signal)
    except Exception:
        db.rollback()
        raise

    readiness_pct, _ = compute_readiness(db, user.id)
    return DiscoveryResultResponse(
        insight_text=insight_text,
        new_signals=[BlueprintSignalOut.model_validate(signal) for signal in created],
        readiness_pct=readiness_pct,
    )
