"""
Operation A — Conversation (PRD section 31).
The AI behaves like a thoughtful matchmaker while deliberately filling the
missing pieces of BOTH sides of the Relationship Blueprint.
"""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import settings
from ..llm import get_chat_llm
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
2. Create atomic observations from the LATEST user turn only. Each observation must have the correct perspective/category, a concise label, strength, confidence, explicit/inferred status, and short evidence. Preserve tensions and contradictions as separate observations instead of smoothing them away. Never make an inferred observation a hard requirement.
3. Re-read the available conversation working memory and populate coverage_fields with every perspective-specific field genuinely supported. A field is covered only when there is concrete enough evidence to become a Blueprint signal.
4. Decide whether both sides have enough depth. A side has enough depth when personality, lifestyle, and relationship_dynamic are covered, plus at least two of physical_type, love_language, dealbreakers, or values.
5. If either side is not deep enough, choose next_question_target from a genuinely missing field that would most improve the weaker side.
6. Write reply: briefly mirror one or two specific things they just said, then ask exactly ONE natural question aimed at next_question_target.

Important steering rules:
- Every reply must end in a real question unless both perspectives already have enough depth.
- Do not repeat a question about a perspective-specific field that is already covered.
- If an answer is vague, you may deepen that same field with one concrete-example question before marking it covered.
- If the user avoids a question, move to another missing field and revisit later only if needed.
- One question at a time. Never list questions or announce a checklist.
- Keep the tone warm, conversational, perceptive and concise — not clinical, therapeutic, or an assessment.
- Values and dealbreakers should emerge naturally.
- Never infer facts the user did not give you.

When both sides have enough depth, next_question_target may be null and the reply can say that Anaphora has enough for a first Blueprint. It can still invite the user to add more later."""

MINIMUM_USER_TURNS = 4
MAXIMUM_USER_TURNS = 16


def _message_content_for_model(message: dict) -> str:
    """Use compact processing memory for long turns while retaining raw text in DB."""
    return message.get("processing_summary") or message.get("content", "")


def _to_langchain_messages(history: list[dict]) -> list:
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in history:
        content = _message_content_for_model(m)
        if m["role"] == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    return messages


def _known_coverage_note(known_me: set[str], known_ideal: set[str]) -> str:
    if not known_me and not known_ideal:
        return ""

    def _fmt(categories: set[str]) -> str:
        return ", ".join(sorted(categories)) if categories else "nothing yet"

    return f"""

This is a follow-up conversation — the user already has a Blueprint from earlier conversations and/or Discoveries. Already known (do NOT re-ask about these categories on that side; judge next_question_target and enough depth against this PLUS what you learn now):
- ME already covers: {_fmt(known_me)}
- IDEAL_PARTNER already covers: {_fmt(known_ideal)}
If one side is already far more complete than the other, spend this conversation on the weaker side."""


def converse(history: list[dict], known_me: set[str] = frozenset(), known_ideal: set[str] = frozenset()) -> ConversationTurnResult:
    """Steer from compact working memory while returning atomic observations."""
    llm = get_chat_llm(settings.openai_conversation_model, temperature=0.7)
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
    turns = user_turn_count(history)
    if turns < MINIMUM_USER_TURNS:
        return False

    ideal = _side_categories(coverage_fields, "ideal_partner") | known_ideal
    me = _side_categories(coverage_fields, "me") | known_me
    if side_ready(ideal) and side_ready(me):
        return True
    return turns >= MAXIMUM_USER_TURNS
