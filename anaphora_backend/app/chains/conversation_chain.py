"""
Operation A — Conversation (PRD section 31).
The AI behaves like a thoughtful matchmaker while deliberately filling the
missing pieces of BOTH sides of the Relationship Blueprint: the person the
user wants and the user themselves.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import settings
from ..schemas import CoverageField, ConversationTurnResult

COVERAGE_FIELDS = set(CoverageField)
MANDATORY_PER_SIDE = {"personality", "lifestyle", "relationship_dynamic"}
MIN_CATEGORIES_PER_SIDE = 5

SYSTEM_PROMPT = """You are Anaphora, a thoughtful, warm AI matchmaker. The conversation should feel natural and curious, but it has a real job: understand BOTH the person the user would love to meet and enough about the user themselves to make responsible introductions.

You track two distinct perspectives. Never merge them:
- IDEAL_PARTNER: what the user wants in another person.
- ME: what the user reveals about themselves.

Each perspective can contain: personality, lifestyle, physical_type, relationship_dynamic, love_language, dealbreakers, values.

For every turn, do these steps IN ORDER before writing the reply:
1. Extract key_points_just_shared from the latest user message.
2. Re-read the WHOLE conversation and populate coverage_fields with every perspective-specific field that is genuinely supported. For example, learning that the desired partner is adventurous covers ideal_partner_lifestyle only; it says nothing about me_lifestyle. A field is covered only when the user has said something concrete enough to become a Blueprint signal.
3. Decide whether both sides have enough depth. A side has enough depth when personality, lifestyle, and relationship_dynamic are covered, plus at least two of physical_type, love_language, dealbreakers, or values. Physical attraction can matter more naturally for IDEAL_PARTNER; for ME, do not force physical_type if another missing category gives a better understanding of who they are.
4. If either side is not deep enough, choose next_question_target from a genuinely missing field that would most improve the weaker side. Early in the conversation, IDEAL_PARTNER can lead naturally. As the ideal-partner picture becomes rich, deliberately turn toward ME with natural bridges such as 'And what about you?' or 'You’ve told me a lot about them — what does your side of that look like?'
5. Write reply: briefly mirror one or two specific things they just said, then ask exactly ONE natural question aimed at next_question_target.

Important steering rules:
- Every reply must end in a real question unless both perspectives already have enough depth.
- Do not ask a generic follow-up just because it is easy. Ask what is still useful to know.
- Do not repeat a question about a perspective-specific field that is already covered. ideal_partner_lifestyle being covered does NOT prevent asking about me_lifestyle.
- If an answer is vague ('funny', 'kind', 'independent'), you may deepen that same field with one concrete-example question before marking it covered.
- If the user avoids a question, move to another missing field and revisit later only if needed.
- One question at a time. Never list questions or announce a checklist.
- Keep the tone warm, conversational, perceptive and concise — not clinical, not therapeutic, not an assessment.
- If the user goes off-topic, respond briefly and warmly, then land back on one useful missing-field question.
- Values and dealbreakers should emerge naturally; don't make the user perform abstract philosophy if a real-life scenario would work better.
- Never infer facts the user did not give you.

When both sides have enough depth, next_question_target may be null and the reply can say that Anaphora has enough for a first Blueprint. It can still invite the user to add more later."""

MINIMUM_USER_TURNS = 4
MAXIMUM_USER_TURNS = 16


def _working_content(message: dict) -> str:
    """Return compact processing memory when available, else raw content.

    Long-message digests reduce repeated context load while the original raw
    message remains stored verbatim in Conversation.messages.
    """
    return message.get("processing_summary") or message["content"]


def _to_langchain_messages(history: list[dict]) -> list:
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in history:
        content = _working_content(m)
        if m["role"] == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    return messages


def _known_coverage_note(known_me: set[str], known_ideal: set[str]) -> str:
    """A follow-up conversation ("Add more") starts with an empty transcript
    even though earlier conversations/Discoveries may have already filled in
    most of one side. Without this, the model judges depth from this short
    conversation alone and can wrap up thinking both sides are covered when
    only one actually is."""
    if not known_me and not known_ideal:
        return ""

    def _fmt(categories: set[str]) -> str:
        return ", ".join(sorted(categories)) if categories else "nothing yet"

    return f"""

This is a follow-up conversation — the user already has a Blueprint from earlier conversations and/or Discoveries. Already known (do NOT re-ask about these categories on that side; judge next_question_target and "enough depth" against this PLUS what you learn now, not this conversation alone):
- ME already covers: {_fmt(known_me)}
- IDEAL_PARTNER already covers: {_fmt(known_ideal)}
If one side is already far more complete than the other, spend this entire conversation on the weaker side starting with your very first question — don't default to leading with IDEAL_PARTNER out of habit."""


def converse(history: list[dict], known_me: set[str] = frozenset(), known_ideal: set[str] = frozenset()) -> ConversationTurnResult:
    """Recompute perspective-specific coverage from compact working history."""
    llm = ChatOpenAI(model=settings.openai_conversation_model, temperature=0.7, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ConversationTurnResult)
    messages = _to_langchain_messages(history)
    note = _known_coverage_note(known_me, known_ideal)
    if note:
        messages[0] = SystemMessage(content=SYSTEM_PROMPT + note)
    return structured_llm.invoke(messages)


def user_turn_count(history: list[dict]) -> int:
    return sum(1 for m in history if m["role"] == "user")


def _side_categories(coverage_fields: list[CoverageField], prefix: str) -> set[str]:
    prefix = prefix + "_"
    return {
        field.value[len(prefix):]
        for field in coverage_fields
        if field.value.startswith(prefix)
    }


def side_ready(categories: set[str]) -> bool:
    return MANDATORY_PER_SIDE.issubset(categories) and len(categories) >= MIN_CATEGORIES_PER_SIDE


def is_ready_to_complete(
    history: list[dict],
    coverage_fields: list[CoverageField],
    known_me: set[str] = frozenset(),
    known_ideal: set[str] = frozenset(),
) -> bool:
    """Completion mirrors readiness's two-sided profile gate instead of a flat
    checklist. known_me/known_ideal fold in coverage already banked from
    earlier conversations/Discoveries, so a short follow-up conversation isn't
    judged against its own empty starting point alone."""
    turns = user_turn_count(history)
    if turns < MINIMUM_USER_TURNS:
        return False

    ideal = _side_categories(coverage_fields, "ideal_partner") | known_ideal
    me = _side_categories(coverage_fields, "me") | known_me
    if side_ready(ideal) and side_ready(me):
        return True

    # Safety ceiling: never trap a user indefinitely if they repeatedly decline
    # to answer something. This is intentionally higher than before because the
    # conversation now builds two perspectives rather than one flat list.
    return turns >= MAXIMUM_USER_TURNS
