from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Conversation, BlueprintSignal
from ..schemas import (
    ConversationStartResponse, ConversationMessageRequest, ConversationMessageResponse,
    ConversationCompleteRequest, ConversationCompleteResponse, BlueprintSignalOut, PerspectiveBlueprint,
)
from ..chains.conversation_chain import converse, user_turn_count, is_ready_to_complete, COMPLETION_MESSAGE
from ..chains.extraction_chain import extract_blueprint
from ..readiness import compute_readiness

router = APIRouter(prefix="/conversation", tags=["conversation"])

OPENING_PROMPT = "Tell me about the person you'd love to meet."


@router.post("/start", response_model=ConversationStartResponse)
def start_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = Conversation(user_id=user.id, messages=[{"role": "assistant", "content": OPENING_PROMPT}])
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return ConversationStartResponse(conversation_id=convo.id, message=OPENING_PROMPT)


@router.post("/message", response_model=ConversationMessageResponse)
def send_message(
    body: ConversationMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convo = db.get(Conversation, body.conversation_id)
    if not convo or convo.user_id != user.id:
        raise HTTPException(404, "Conversation not found")
    if convo.status == "completed":
        raise HTTPException(400, "Conversation already completed")

    history = list(convo.messages)
    history.append({"role": "user", "content": body.message})

    turn = converse(history)
    history.append({"role": "assistant", "content": turn.reply})

    convo.messages = history
    db.add(convo)
    db.commit()

    return ConversationMessageResponse(
        reply=turn.reply,
        turn_count=user_turn_count(history),
        ready_to_complete=is_ready_to_complete(history, turn.categories_covered),
        categories_covered=turn.categories_covered,
    )


@router.post("/complete", response_model=ConversationCompleteResponse)
def complete_conversation(
    body: ConversationCompleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convo = db.get(Conversation, body.conversation_id)
    if not convo or convo.user_id != user.id:
        raise HTTPException(404, "Conversation not found")
    if convo.status == "completed":
        raise HTTPException(400, "Conversation already completed — signals were already extracted")

    result = extract_blueprint(convo.messages)

    # The Blueprint should reflect the latest conversation extraction, not
    # accumulate duplicates across repeated completions. Clear prior
    # conversation-sourced signals before inserting the new set — leave
    # discovery-sourced signals untouched, since those come from a
    # separate flow (PRD section 13: source = "conversation" | "discovery").
    db.query(BlueprintSignal).filter(
        BlueprintSignal.user_id == user.id,
        BlueprintSignal.source == "conversation",
    ).delete()

    created: list[BlueprintSignal] = []

    def _store(perspective: str, category: str, items) -> None:
        for item in items:
            signal = BlueprintSignal(
                user_id=user.id,
                perspective=perspective,
                category=category,
                label=item.label,
                strength=item.strength.value,
                source="conversation",
                evidence_text=item.evidence_text,
            )
            db.add(signal)
            created.append(signal)

    # Both perspectives share the same 7 categories (schemas.PerspectiveBlueprint).
    for category in PerspectiveBlueprint.model_fields:
        _store("IDEAL_PARTNER", category, getattr(result.ideal_partner, category))
        _store("ME", category, getattr(result.me, category))

    user.blueprint_narrative = result.narrative
    db.add(user)

    convo.status = "completed"
    db.add(convo)
    db.commit()
    for s in created:
        db.refresh(s)

    readiness_pct, _ = compute_readiness(db, user.id)

    return ConversationCompleteResponse(
        signals=[BlueprintSignalOut.model_validate(s) for s in created],
        narrative=result.narrative,
        readiness_pct=readiness_pct,
    )
