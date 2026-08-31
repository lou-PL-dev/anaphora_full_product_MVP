from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Conversation, BlueprintSignal
from ..schemas import (
    ConversationStartResponse, ConversationMessageRequest, ConversationMessageResponse,
    ConversationCompleteRequest, ConversationCompleteResponse, BlueprintSignalOut, PerspectiveBlueprint,
)
from ..chains.conversation_chain import converse, user_turn_count, is_ready_to_complete
from ..chains.extraction_chain import extract_blueprint
from ..readiness import compute_readiness

router = APIRouter(prefix="/conversation", tags=["conversation"])
OPENING_PROMPT = "Tell me about the person you'd love to meet."


@router.post("/start", response_model=ConversationStartResponse)
def start_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = Conversation(user_id=user.id, messages=[{"role": "assistant", "content": OPENING_PROMPT}])
    db.add(convo); db.commit(); db.refresh(convo)
    return ConversationStartResponse(conversation_id=convo.id, message=OPENING_PROMPT)


@router.post("/message", response_model=ConversationMessageResponse)
def send_message(body: ConversationMessageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.get(Conversation, body.conversation_id)
    if not convo or convo.user_id != user.id: raise HTTPException(404, "Conversation not found")
    if convo.status == "completed": raise HTTPException(400, "Conversation already completed")
    history = list(convo.messages)
    history.append({"role": "user", "content": body.message})
    turn = converse(history)
    history.append({"role": "assistant", "content": turn.reply})
    convo.messages = history; db.add(convo); db.commit()
    return ConversationMessageResponse(reply=turn.reply, turn_count=user_turn_count(history), ready_to_complete=is_ready_to_complete(history, turn.coverage), coverage=turn.coverage)


def _normalise_label(label: str) -> str:
    return " ".join(label.lower().strip().split())


@router.post("/complete", response_model=ConversationCompleteResponse)
def complete_conversation(body: ConversationCompleteRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.get(Conversation, body.conversation_id)
    if not convo or convo.user_id != user.id: raise HTTPException(404, "Conversation not found")
    if convo.status == "completed": raise HTTPException(400, "Conversation already completed — signals were already extracted")

    result = extract_blueprint(convo.messages)
    existing = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
    existing_keys = {(s.perspective, s.category, _normalise_label(s.label)) for s in existing}

    def _store(perspective: str, category: str, items) -> None:
        for item in items:
            key = (perspective, category, _normalise_label(item.label))
            if key in existing_keys: continue
            db.add(BlueprintSignal(user_id=user.id, perspective=perspective, category=category, label=item.label, strength=item.strength.value, source="conversation", evidence_text=item.evidence_text))
            existing_keys.add(key)

    for category in PerspectiveBlueprint.model_fields:
        _store("IDEAL_PARTNER", category, getattr(result.ideal_partner, category))
        _store("ME", category, getattr(result.me, category))

    user.blueprint_narrative = result.narrative
    db.add(user); convo.status = "completed"; db.add(convo); db.commit()

    # Return the complete conversation-sourced layer so clients can replace
    # their local conversation layer atomically while retaining Discovery data.
    conversation_signals = db.query(BlueprintSignal).filter(
        BlueprintSignal.user_id == user.id,
        BlueprintSignal.source == "conversation",
    ).all()
    readiness_pct, _ = compute_readiness(db, user.id)
    return ConversationCompleteResponse(
        signals=[BlueprintSignalOut.model_validate(s) for s in conversation_signals],
        narrative=result.narrative,
        readiness_pct=readiness_pct,
    )
