from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, DiscoveryResponse, BlueprintEvidence
from ..schemas import DiscoveryResponseIn, DiscoveryResultResponse, BlueprintSignalOut
from ..discovery_registry import DISCOVERIES, get_discovery_spec
from ..blueprint_canonicalizer import (
    add_evidence,
    ensure_evidence_backfill,
    rebuild_blueprint,
    signals_supported_by,
)
from ..readiness import compute_readiness

router = APIRouter(prefix="/discovery", tags=["discovery"])


def _spec_or_404(discovery_id: str):
    spec = get_discovery_spec(discovery_id)
    if spec is None or spec.status != "active":
        raise HTTPException(404, "Discovery not found")
    return spec


@router.get("")
def list_discoveries(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completed_ids = {
        row.discovery_id
        for row in db.query(DiscoveryResponse.discovery_id)
        .filter(DiscoveryResponse.user_id == user.id)
        .distinct()
    }
    return [
        {
            "id": spec.id, "title": spec.title, "status": spec.status,
            "question_count": len(spec.questions), "completed": spec.id in completed_ids,
        }
        for spec in DISCOVERIES.values()
        if spec.status == "active"
    ]


@router.get("/{discovery_id}")
def get_discovery(discovery_id: str):
    spec = _spec_or_404(discovery_id)
    public_questions = [
        {key: value for key, value in question.items() if key not in {"perspective", "category"}}
        for question in spec.questions
    ]
    return {"id": spec.id, "title": spec.title, "questions": public_questions}


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

    insight_text = spec.synthesize_insight(responses_map)
    new_signal_items = spec.responses_to_signals(responses_map)
    source_key = f"discovery:{discovery_id}"

    try:
        ensure_evidence_backfill(db, user.id)
        db.query(DiscoveryResponse).filter(
            DiscoveryResponse.user_id == user.id,
            DiscoveryResponse.discovery_id == discovery_id,
        ).delete(synchronize_session=False)

        # Rerunning a Discovery replaces only that source's raw observations.
        # The full canonical projection is rebuilt below.
        db.query(BlueprintEvidence).filter(
            BlueprintEvidence.user_id == user.id,
            BlueprintEvidence.source == source_key,
        ).delete(synchronize_session=False)
        # Backward-compatible cleanup for the original MVP Discovery, whose
        # old signals used the generic source="discovery".
        if discovery_id == "life_you_are_building":
            db.query(BlueprintEvidence).filter(
                BlueprintEvidence.user_id == user.id,
                BlueprintEvidence.source == "discovery",
                BlueprintEvidence.category == spec.category,
            ).delete(synchronize_session=False)

        for item in body:
            db.add(DiscoveryResponse(
                user_id=user.id,
                discovery_id=discovery_id,
                question_id=item.question_id,
                response=item.response,
            ))

        created_evidence_ids: set[str] = set()
        for mapped in new_signal_items:
            item = mapped.item
            if not item.label.strip():
                continue
            evidence = add_evidence(
                db,
                user_id=user.id,
                perspective=mapped.perspective,
                category=mapped.category,
                label=item.label,
                strength=item.strength.value,
                source=source_key,
                evidence_text=item.evidence_text,
                confidence=item.confidence,
                explicit=item.explicit,
            )
            created_evidence_ids.add(evidence.id)

        canonical_signals = rebuild_blueprint(db, user)
        created = signals_supported_by(canonical_signals, created_evidence_ids)
        db.commit()
    except Exception:
        db.rollback()
        raise

    readiness_pct, _ = compute_readiness(db, user.id)
    return DiscoveryResultResponse(
        insight_text=insight_text,
        new_signals=[BlueprintSignalOut.model_validate(signal) for signal in created],
        readiness_pct=readiness_pct,
    )
