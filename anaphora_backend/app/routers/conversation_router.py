from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Conversation, BlueprintSignal
from ..schemas import (
    ConversationStartResponse, ConversationMessageRequest, ConversationMessageResponse,
    ConversationCompleteRequest, ConversationCompleteResponse, BlueprintSignalOut, PerspectiveBlueprint,
)
from ..chains.conversation_chain import converse, user_turn_count, is_ready_to_complete, side_ready
from ..chains.extraction_chain import extract_blueprint
from ..chains.input_segmentation import is_long_input
from ..chains.long_input_chain import digest_long_input, format_processing_summary
from ..readiness import compute_readiness, category_coverage

router = APIRouter(prefix="/conversation", tags=["conversation"])

OPENING_PROMPT = "Tell me about the person you'd love to meet."
OPENING_PROMPT_ME_FOCUSED = (
    "You've already told Anaphora a lot about who you're looking for — "
    "let's talk about you this time. What does your own day-to-day look like?"
)


@router.post("/start", response_model=ConversationStartResponse)
def start_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
    known_me, known_ideal = category_coverage(signals)
    # A follow-up "Add more" conversation shouldn't default to asking about
    # the ideal partner again if that side is already the well-covered one.
    opening = OPENING_PROMPT_ME_FOCUSED if side_ready(known_ideal) and not side_ready(known_me) else OPENING_PROMPT

    convo = Conversation(user_id=user.id, messages=[{"role": "assistant", "content": opening}])
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return ConversationStartResponse(conversation_id=convo.id, message=opening)


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

    signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user.id).all()
    known_me, known_ideal = category_coverage(signals)

    history = list(convo.messages)
    user_message = {"role": "user", "content": body.message}
    if is_long_input(body.message):
        digest = digest_long_input(body.message)
        user_message["processing_summary"] = format_processing_summary(digest)
    history.append(user_message)

    turn = converse(history, known_me=known_me, known_ideal=known_ideal)
    history.append({"role": "assistant", "content": turn.reply})

    convo.messages = history
    db.add(convo)
    db.commit()

    return ConversationMessageResponse(
        reply=turn.reply,
        turn_count=user_turn_count(history),
        ready_to_complete=is_ready_to_complete(history, turn.coverage_fields, known_me=known_me, known_ideal=known_ideal),
        categories_covered=turn.coverage_fields,
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

    # Multiple conversations (the "Add more" flow) each cover their own
    # ground — a follow-up conversation about values shouldn't erase what
    # an earlier one established about lifestyle. Replace only the
    # (perspective, category) pairs this extraction actually has fresh
    # data for, and leave every other conversation-sourced signal alone.
    created: list[BlueprintSignal] = []

    def _store(perspective: str, category: str, items) -> None:
        if not items:
            return
        db.query(BlueprintSignal).filter(
            BlueprintSignal.user_id == user.id,
            BlueprintSignal.source == "conversation",
            BlueprintSignal.perspective == perspective,
            BlueprintSignal.category == category,
        ).delete()
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

    for category in PerspectiveBlueprint.model_fields:
        _store("IDEAL_PARTNER", category, getattr(result.ideal_partner, category))
        _store("ME", category, getattr(result.me, category))

    # Same reasoning for the narrative: a follow-up conversation's summary
    # should add to the Blueprint narrative, not replace it outright.
    user.blueprint_narrative = (
        f"{user.blueprint_narrative}\n\n{result.narrative}"
        if user.blueprint_narrative else result.narrative
    )
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
