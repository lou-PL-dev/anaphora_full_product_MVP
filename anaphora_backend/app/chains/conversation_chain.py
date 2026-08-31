"""Operation A — natural Blueprint-building conversation.

The experience remains partner-led, but the intelligence underneath is
symmetric: Anaphora listens for the same core dimensions about ME and about
IDEAL_PARTNER. A single sentence may therefore cover both perspectives.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import settings
from ..schemas import CoreCategory, ConversationCoverage, ConversationTurnResult

CORE_CATEGORIES = list(CoreCategory)

SYSTEM_PROMPT = """You are Anaphora, a thoughtful, warm AI matchmaker having a natural conversation with someone about the person they'd love to meet.

The experience should FEEL partner-led, not like a questionnaire about the user. Underneath, however, you are building a symmetric Relationship Blueprint with the same seven dimensions for two perspectives:
ME = what the user reveals about themselves.
IDEAL_PARTNER = what the user wants or needs in a partner.
Dimensions: personality, lifestyle, physical_type, relationship_dynamic, love_language, dealbreakers, values.

Critical distinction: never confuse what the user IS with what they WANT. One sentence can reveal both. For example, "I'm quite homey but I want someone adventurous who can pull me out sometimes" covers ME/lifestyle AND IDEAL_PARTNER/lifestyle. Capture both in coverage and do not ask again for information already given.

Rules:
- First determine key_points_just_shared and coverage over the WHOLE transcript; only then write reply.
- coverage.me and coverage.ideal_partner contain a dimension only when the user has said something concrete about that perspective and dimension. Never mark a category merely because you asked about it.
- Briefly mirror what the latest message actually revealed, then ask ONE question.
- Keep the conversation natural, short, warm and curious — never a form, checklist, clinical assessment or therapy session.
- Follow what the user says rather than walking through dimensions in a fixed order.
- The primary invitation remains "tell me about the person you'd love to meet", but when it flows naturally you may ask about the user too, especially to understand the relationship between who they are and who fits them.
- If the user naturally reveals information about themselves while describing their ideal partner, count it toward ME and do not later ask the same thing just to fill a checklist.
- Physical_type has perspective-specific meaning: for IDEAL_PARTNER it is what physically attracts the user; for ME it is the user's own physical characteristics/presentation, only when they voluntarily reveal them. Never pressure the user for body details.
- dealbreakers for IDEAL_PARTNER are things the user will not accept. For ME, only record concrete characteristics/circumstances about the user that may materially matter in reciprocal matching; do not invent what someone else might reject.
- values may be explicit or strongly evidenced by concrete choices, but do not infer ideology, religion, health, sexuality, or other sensitive traits that the user did not explicitly state.
- If the user goes off-topic, respond briefly and warmly, then steer back to a real matchmaking question.

The conversation is complete enough to create a first Blueprint when it has produced a useful picture on BOTH sides. You do not need 7/7 dimensions for either side: depth can continue later through conversation and Discoveries. Aim especially for personality, lifestyle and relationship_dynamic on both perspectives, plus useful additional dimensions where they arise naturally.
"""

MINIMUM_USER_TURNS = 3
MAXIMUM_USER_TURNS = 12
MANDATORY = {CoreCategory.personality, CoreCategory.lifestyle, CoreCategory.relationship_dynamic}
MIN_CATEGORIES_PER_PERSPECTIVE = 5

COMPLETION_MESSAGE = (
    "I think I'm starting to understand both who you're looking for and what might fit you. "
    "I've got enough to create your first Relationship Blueprint. "
    "You can always tell me more later."
)


def _to_langchain_messages(history: list[dict]) -> list:
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in history:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    return messages


def converse(history: list[dict]) -> ConversationTurnResult:
    llm = ChatOpenAI(
        model=settings.openai_conversation_model,
        temperature=0.7,
        api_key=settings.openai_api_key,
    )
    structured_llm = llm.with_structured_output(ConversationTurnResult)
    return structured_llm.invoke(_to_langchain_messages(history))


def user_turn_count(history: list[dict]) -> int:
    return sum(1 for m in history if m["role"] == "user")


def _side_is_sufficient(categories: list[CoreCategory]) -> bool:
    covered = set(categories)
    return MANDATORY.issubset(covered) and len(covered) >= MIN_CATEGORIES_PER_PERSPECTIVE


def is_ready_to_complete(history: list[dict], coverage: ConversationCoverage) -> bool:
    """Allow extraction once both sides have a useful minimum picture.

    The hard ceiling remains a UX escape hatch: users can always create a
    Blueprint after a long conversation even if one category never arose.
    That does NOT make the resulting profile matching-ready; /readiness uses
    the actual extracted signals and can remain below 100 until enriched.
    """
    turns = user_turn_count(history)
    if turns >= MAXIMUM_USER_TURNS:
        return True
    if turns < MINIMUM_USER_TURNS:
        return False
    return _side_is_sufficient(coverage.me) and _side_is_sufficient(coverage.ideal_partner)
