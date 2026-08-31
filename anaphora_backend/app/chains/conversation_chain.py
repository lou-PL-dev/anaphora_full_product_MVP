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


def _to_langchain_messages(history: list[dict]) -> list:
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in history:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    return messages


def converse(history: list[dict]) -> ConversationTurnResult:
    """Recompute perspective-specific coverage from the full transcript every turn."""
    llm = ChatOpenAI(model=settings.openai_conversation_model, temperature=0.7, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ConversationTurnResult)
    return structured_llm.invoke(_to_langchain_messages(history))


def user_turn_count(history: list[dict]) -> int:
    return sum(1 for m in history if m["role"] == "user")


def _side_categories(coverage_fields: list[CoverageField], prefix: str) -> set[str]:
    prefix = prefix + "_"
    return {
        field.value[len(prefix):]
        for field in coverage_fields
        if field.value.startswith(prefix)
    }


def _side_ready(categories: set[str]) -> bool:
    return MANDATORY_PER_SIDE.issubset(categories) and len(categories) >= MIN_CATEGORIES_PER_SIDE


def is_ready_to_complete(history: list[dict], coverage_fields: list[CoverageField]) -> bool:
    """Completion mirrors readiness's two-sided profile gate instead of a flat checklist."""
    turns = user_turn_count(history)
    if turns < MINIMUM_USER_TURNS:
        return False

    ideal = _side_categories(coverage_fields, "ideal_partner")
    me = _side_categories(coverage_fields, "me")
    if _side_ready(ideal) and _side_ready(me):
        return True

    # Safety ceiling: never trap a user indefinitely if they repeatedly decline
    # to answer something. This is intentionally higher than before because the
    # conversation now builds two perspectives rather than one flat list.
    return turns >= MAXIMUM_USER_TURNS
