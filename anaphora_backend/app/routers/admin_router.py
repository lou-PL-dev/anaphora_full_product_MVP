"""Tiny private research API for the MVP tester round.

Normal product events are written with the anonymous per-device user id.
Admin reads and destructive reset actions require one shared secret supplied
through X-Admin-Secret and configured as ADMIN_SECRET on the backend.
"""
from __future__ import annotations

import hmac
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import settings
from ..database import get_db
from ..models import (
    BlueprintEvidence,
    BlueprintSignal,
    Conversation,
    DiscoveryResponse,
    FriendInvite,
    FriendResponse,
    FriendSignal,
    TesterEvent,
    User,
)
from ..readiness import compute_readiness

router = APIRouter(tags=["tester-research"])


class EventIn(BaseModel):
    event: str = Field(min_length=1, max_length=80)
    metadata: dict[str, Any] = Field(default_factory=dict)


def _require_admin(x_admin_secret: str = Header("", alias="X-Admin-Secret")) -> None:
    if not settings.admin_secret:
        raise HTTPException(503, "ADMIN_SECRET is not configured")
    if not hmac.compare_digest(x_admin_secret, settings.admin_secret):
        raise HTTPException(401, "Invalid admin secret")


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


@router.post("/events", status_code=204)
def record_event(
    body: EventIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.add(TesterEvent(user_id=user.id, event=body.event, metadata_json=body.metadata))
    db.commit()
    return None


@router.get("/admin/test-sessions")
def list_test_sessions(
    _admin: None = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).limit(200).all()
    rows = []
    for user in users:
        conversations = db.query(Conversation).filter(Conversation.user_id == user.id).all()
        events = db.query(TesterEvent).filter(TesterEvent.user_id == user.id).all()
        discoveries = db.query(DiscoveryResponse).filter(DiscoveryResponse.user_id == user.id).all()
        signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
        readiness, _ = compute_readiness(db, user.id)

        activity_times = [user.created_at]
        activity_times.extend(c.created_at for c in conversations if c.created_at)
        activity_times.extend(e.created_at for e in events if e.created_at)
        activity_times.extend(d.created_at for d in discoveries if d.created_at)
        last_activity = max((x for x in activity_times if x), default=user.created_at)
        turn_count = sum(
            1 for c in conversations for message in (c.messages or []) if message.get("role") == "user"
        )
        discovery_ids = sorted({d.discovery_id for d in discoveries})

        rows.append({
            "user_id": user.id,
            "started_at": _iso(user.created_at),
            "last_activity": _iso(last_activity),
            "readiness": readiness,
            "conversation_count": len(conversations),
            "turn_count": turn_count,
            "signal_count": len(signals),
            "discoveries_completed": len(discovery_ids),
            "intros_opened": any(e.event == "intros_opened" for e in events),
            "match_returned": any(e.event == "match_returned" for e in events),
        })

    rows.sort(key=lambda row: row["last_activity"] or "", reverse=True)
    return {"sessions": rows}


@router.delete("/admin/test-sessions")
def clear_test_sessions(
    _admin: None = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Clear tester-generated data while preserving candidates/discoveries.

    Delete in dependency order because the MVP schema intentionally keeps
    foreign keys simple and does not rely on DB-level cascade deletes.
    """
    try:
        friend_response_ids = [row[0] for row in db.query(FriendResponse.id).all()]
        if friend_response_ids:
            db.query(FriendSignal).filter(FriendSignal.response_id.in_(friend_response_ids)).delete(synchronize_session=False)
        db.query(FriendResponse).delete(synchronize_session=False)
        db.query(FriendInvite).delete(synchronize_session=False)
        db.query(TesterEvent).delete(synchronize_session=False)
        db.query(DiscoveryResponse).delete(synchronize_session=False)
        db.query(BlueprintEvidence).delete(synchronize_session=False)
        db.query(BlueprintSignal).delete(synchronize_session=False)
        db.query(Conversation).delete(synchronize_session=False)
        deleted_users = db.query(User).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"cleared": True, "deleted_users": deleted_users}


@router.get("/admin/test-sessions/{user_id}")
def get_test_session(
    user_id: str,
    _admin: None = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Tester not found")

    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.asc())
        .all()
    )
    signals = (
        db.query(BlueprintSignal)
        .filter(BlueprintSignal.user_id == user_id)
        .order_by(BlueprintSignal.created_at.asc())
        .all()
    )
    discoveries = (
        db.query(DiscoveryResponse)
        .filter(DiscoveryResponse.user_id == user_id)
        .order_by(DiscoveryResponse.created_at.asc())
        .all()
    )
    events = (
        db.query(TesterEvent)
        .filter(TesterEvent.user_id == user_id)
        .order_by(TesterEvent.created_at.asc())
        .all()
    )
    readiness, breakdown = compute_readiness(db, user_id)

    return {
        "user_id": user.id,
        "started_at": _iso(user.created_at),
        "readiness": readiness,
        "readiness_breakdown": breakdown,
        "blueprint_narrative": user.blueprint_narrative,
        "conversations": [
            {
                "id": c.id,
                "status": c.status,
                "created_at": _iso(c.created_at),
                "messages": c.messages or [],
            }
            for c in conversations
        ],
        "signals": [
            {
                "id": s.id,
                "perspective": s.perspective,
                "category": s.category,
                "label": s.label,
                "strength": s.strength,
                "source": s.source,
                "evidence_text": s.evidence_text,
                "confidence": s.confidence,
                "created_at": _iso(s.created_at),
            }
            for s in signals
        ],
        "discoveries": [
            {
                "discovery_id": d.discovery_id,
                "question_id": d.question_id,
                "response": d.response,
                "created_at": _iso(d.created_at),
            }
            for d in discoveries
        ],
        "events": [
            {
                "event": e.event,
                "metadata": e.metadata_json or {},
                "created_at": _iso(e.created_at),
            }
            for e in events
        ],
    }


@router.get("/admin/test-sessions/{user_id}/matches-debug")
def get_matches_debug(
    user_id: str,
    _admin: None = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Why a tester saw no matches — real pipeline numbers, not a guess.

    Runs the same eligibility + retrieval + reranking stages as GET
    /matches, but reports the count/scores at each stage instead of only
    the final result, and skips the relationship-reasoning LLM call (the
    deterministic stages already show whether anything would even reach
    it). Requires readiness — deliberately does NOT bypass that gate, so
    the numbers reflect exactly what the member's own /matches call sees.
    """
    from ..chains.matching_chain_v5 import debug_find_matches
    from ..routers.matching_router import _preferred_age_bounds

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Tester not found")

    readiness, _breakdown = compute_readiness(db, user_id)
    if readiness < 100:
        return {"readiness": readiness, "error": "Readiness is below 100% — /matches never attempts matching yet."}

    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user_id).all()
    age_min, age_max = _preferred_age_bounds(user.preferred_age_range)
    result = debug_find_matches(
        db,
        [s for s in signals if s.perspective == "IDEAL_PARTNER"],
        user_me_signals=[s for s in signals if s.perspective == "ME"],
        user_us_signals=[s for s in signals if s.perspective == "US"],
        gender_preference=user.gender_preference,
        age_min=age_min,
        age_max=age_max,
        user_gender=user.gender,
        user_age=user.age,
        user_id=user.id,
    )
    result["readiness"] = readiness
    result["user_own_demographics"] = {"gender": user.gender, "age": user.age}
    result["user_stated_preference"] = {"gender_preference": user.gender_preference, "age_min": age_min, "age_max": age_max}
    return result
