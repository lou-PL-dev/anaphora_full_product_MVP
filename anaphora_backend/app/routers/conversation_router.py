from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Conversation, BlueprintSignal
from ..schemas import (
    ConversationStartResponse, ConversationMessageRequest, ConversationMessageResponse,
    ConversationCompleteRequest, ConversationCompleteResponse, BlueprintSignalOut,
    PerspectiveBlueprint, IdealPartnerBlueprint, RelationshipBlueprint,
)
from ..chains.conversation_chain import converse, user_turn_count, is_ready_to_complete
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
    known_me, known_ideal, known_us = category_coverage(signals)
    opening = OPENING_PROMPT_ME_FOCUSED if len(known_ideal) >= 3 and len(known_me) < 3 else OPENING_PROMPT

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
    known_me, known_ideal, known_us = category_coverage(signals)

    history = list(convo.messages)
    user_message = {"role": "user", "content": body.message}
    long_digest = None
    if is_long_input(body.message):
        long_digest = digest_long_input(body.message)
        user_message["processing_summary"] = format_processing_summary(long_digest)
    history.append(user_message)

    turn = converse(history, known_me=known_me, known_ideal=known_ideal, known_us=known_us)

    # Canonical machine memory lives on the original user turn. Long messages
    # use the chunk-aware digest observations; ordinary messages reuse the
    # observations returned by the same conversational LLM call, avoiding an
    # extra extraction request.
    observations = long_digest.observations if long_digest and long_digest.observations else turn.observations
    user_message["observations"] = [obs.model_dump(mode="json") for obs in observations]

    history.append({
        "role": "assistant",
        "content": turn.reply,
        "question_target": turn.next_question_target.value if turn.next_question_target else None,
    })
    convo.messages = history
    db.add(convo)
    db.commit()

    return ConversationMessageResponse(
        reply=turn.reply,
        turn_count=user_turn_count(history),
        ready_to_complete=is_ready_to_complete(history, turn.coverage_fields),
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

    # Reconciliation is now driven by the accumulated structured observations,
    # not by an LLM re-reading and re-summarising the entire raw transcript.
    result = extract_blueprint(convo.messages)
    created: list[BlueprintSignal] = []

    source_key = f"conversation:{convo.id}"

    def _store(perspective: str, category: str, items) -> None:
        if not items:
            return
        existing = {
            (signal.label or "").strip().casefold()
            for signal in db.query(BlueprintSignal).filter(
                BlueprintSignal.user_id == user.id,
                BlueprintSignal.perspective == perspective,
                BlueprintSignal.category == category,
            ).all()
        }
        for item in items:
            key = item.label.strip().casefold()
            if not key or key in existing:
                continue
            signal = BlueprintSignal(
                user_id=user.id,
                perspective=perspective,
                category=category,
                label=item.label,
                strength=item.strength.value,
                source=source_key,
                evidence_text=item.evidence_text,
                confidence=item.confidence,
            )
            db.add(signal)
            created.append(signal)
            existing.add(key)

    for category in IdealPartnerBlueprint.model_fields:
        _store("IDEAL_PARTNER", category, getattr(result.ideal_partner, category))
    for category in PerspectiveBlueprint.model_fields:
        _store("ME", category, getattr(result.me, category))
    for category in RelationshipBlueprint.model_fields:
        _store("US", category, getattr(result.us, category))

    # Narrative is a human-readable projection of this reconciled state. A
    # follow-up conversation adds another projection without deleting earlier
    # structured categories that were not revisited.
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
