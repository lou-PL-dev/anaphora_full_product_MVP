from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..friend_library import FRIEND_QUESTION_IDS, formatted_questions, question_prompt
from ..chains.friend_chain import extract_friend_signals
from ..models import BlueprintSignal, FriendInvite, FriendResponse, FriendSignal, User
from ..readiness import compute_readiness
from ..schemas import (
    BlueprintSignalOut,
    FriendCommitRequest,
    FriendCommitResponse,
    FriendInviteCreateResponse,
    FriendInviteInfo,
    FriendInviteListItem,
    FriendRespondRequest,
    FriendReviewOut,
    FriendSignalOut,
)

router = APIRouter(prefix="/friends", tags=["friends"])

INVITE_LIMIT = 3


@router.post("/invite", response_model=FriendInviteCreateResponse)
def create_invite(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Authenticated: the inviting user requests a fresh, single-use link."""
    count = db.query(FriendInvite).filter(FriendInvite.user_id == user.id).count()
    if count >= INVITE_LIMIT:
        raise HTTPException(400, f"You've used all {INVITE_LIMIT} friend invitations on the free plan.")
    invite = FriendInvite(user_id=user.id)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return FriendInviteCreateResponse(token=invite.id, invite_count=count + 1, invite_limit=INVITE_LIMIT)


@router.get("", response_model=list[FriendInviteListItem])
def list_friend_invites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Authenticated: the inviting user's own invites, for the Friends tab."""
    invites = (
        db.query(FriendInvite)
        .filter(FriendInvite.user_id == user.id)
        .order_by(FriendInvite.created_at.desc())
        .all()
    )
    out = []
    for invite in invites:
        response = db.query(FriendResponse).filter(FriendResponse.invite_id == invite.id).first()
        out.append(FriendInviteListItem(
            id=invite.id,
            status=invite.status,
            friend_name=response.friend_name if response else None,
            reviewed=bool(response.reviewed) if response else False,
            created_at=invite.created_at,
        ))
    return out


@router.get("/{invite_id}/review", response_model=FriendReviewOut)
def get_friend_review(invite_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Authenticated: the paraphrased narrative + candidate signals for one
    answered invite — never the friend's raw answers."""
    invite = db.get(FriendInvite, invite_id)
    if not invite or invite.user_id != user.id:
        raise HTTPException(404, "Invite not found")
    response = db.query(FriendResponse).filter(FriendResponse.invite_id == invite_id).first()
    if not response:
        raise HTTPException(404, "This invite hasn't been answered yet")
    signals = db.query(FriendSignal).filter(FriendSignal.response_id == response.id).all()
    return FriendReviewOut(
        invite_id=invite.id,
        friend_name=response.friend_name,
        narrative=response.narrative or "",
        signals=[FriendSignalOut.model_validate(s) for s in signals],
    )


@router.post("/{invite_id}/commit", response_model=FriendCommitResponse)
def commit_friend_signals(
    invite_id: str,
    body: FriendCommitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Authenticated: the user chose which candidate signals to keep.
    Nothing from a friend ever reaches the Blueprint automatically."""
    invite = db.get(FriendInvite, invite_id)
    if not invite or invite.user_id != user.id:
        raise HTTPException(404, "Invite not found")
    response = db.query(FriendResponse).filter(FriendResponse.invite_id == invite_id).first()
    if not response:
        raise HTTPException(404, "This invite hasn't been answered yet")
    signals = db.query(FriendSignal).filter(FriendSignal.response_id == response.id).all()
    accepted_ids = set(body.accepted_signal_ids)

    created: list[BlueprintSignal] = []
    try:
        for signal in signals:
            if signal.id in accepted_ids:
                signal.status = "accepted"
                blueprint_signal = BlueprintSignal(
                    user_id=user.id,
                    perspective=signal.perspective,
                    category=signal.category,
                    label=signal.label,
                    strength=signal.strength,
                    source="friend",
                    evidence_text=signal.evidence_text,
                )
                db.add(blueprint_signal)
                created.append(blueprint_signal)
            else:
                signal.status = "dismissed"
            db.add(signal)
        response.reviewed = True
        db.add(response)
        db.commit()
        for blueprint_signal in created:
            db.refresh(blueprint_signal)
    except Exception:
        db.rollback()
        raise

    readiness_pct, _ = compute_readiness(db, user.id)
    return FriendCommitResponse(
        added_signals=[BlueprintSignalOut.model_validate(s) for s in created],
        readiness_pct=readiness_pct,
    )


# --- Public endpoints: the friend has no account and no auth header. ---

@router.get("/invite/{token}", response_model=FriendInviteInfo)
def get_invite_info(token: str, db: Session = Depends(get_db)):
    invite = db.get(FriendInvite, token)
    if not invite:
        raise HTTPException(404, "This invite link isn't valid.")
    if invite.status == "answered":
        raise HTTPException(410, "This invite link has already been used.")
    inviter = db.get(User, invite.user_id)
    name = (inviter.name or "").strip() or "your friend"
    return FriendInviteInfo(inviter_name=name, questions=formatted_questions(name))


@router.post("/invite/{token}/respond")
def respond_to_invite(token: str, body: FriendRespondRequest, db: Session = Depends(get_db)):
    invite = db.get(FriendInvite, token)
    if not invite:
        raise HTTPException(404, "This invite link isn't valid.")
    if invite.status == "answered":
        raise HTTPException(410, "This invite link has already been used.")

    inviter = db.get(User, invite.user_id)
    name = (inviter.name or "").strip() or "your friend"

    answers_map: dict[str, str] = {}
    for item in body.answers:
        if item.question_id not in FRIEND_QUESTION_IDS:
            raise HTTPException(400, f"Unknown question: {item.question_id}")
        answers_map[item.question_id] = item.response
    if not answers_map:
        raise HTTPException(400, "At least one answer is required")

    labeled_answers = {question_prompt(qid, name): answer for qid, answer in answers_map.items()}
    result = extract_friend_signals(name, labeled_answers)

    try:
        response = FriendResponse(
            invite_id=invite.id,
            friend_name=body.friend_name.strip(),
            raw_answers=answers_map,
            narrative=result.narrative,
        )
        db.add(response)
        db.flush()
        for obs in result.observations:
            db.add(FriendSignal(
                response_id=response.id,
                perspective=obs.perspective,
                category=obs.category.value,
                label=obs.label,
                strength=obs.strength.value,
                evidence_text=obs.evidence_text,
            ))
        invite.status = "answered"
        db.add(invite)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"status": "ok"}
