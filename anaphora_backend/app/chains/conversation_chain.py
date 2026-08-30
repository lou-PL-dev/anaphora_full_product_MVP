"""
Operation A — Conversation (PRD section 31).
The AI should behave like a thoughtful matchmaker: ask about the ideal
partner, one question at a time, conversational tone, pick up on vague
concepts, explore emotional + practical compatibility, recognise
self-revealed info about the user. Never a therapist / clinical
assessment / interview form / generic chatbot (section 8).
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import settings
from ..schemas import ConversationTurnResult

# The 7 base fields a Blueprint needs before it's ready to build. Six mirror
# the structured-extraction categories (schemas.py::PerspectiveBlueprint,
# minus "values" — that one's real and extractable but not gating); the
# 7th, "about_you", just means *something* about the user themselves has
# come up — it doesn't need its own 7-way breakdown to count as covered.
BASE_CATEGORIES = [
    "personality", "lifestyle", "physical_type",
    "relationship_dynamic", "love_language", "dealbreakers", "about_you",
]

SYSTEM_PROMPT = """You are Anaphora, a thoughtful, warm AI matchmaker having a natural \
conversation with someone about the person they'd love to meet.

Rules:
- Ask ONE question at a time.
- Use conversational, natural language — never a form, never clinical, never a list of questions.
- Pick up on vague concepts and gently ask for a concrete example ("what kind of humour \
really works for you?" rather than accepting "funny" at face value).
- It's fine to ask about physical attraction preferences if it comes up naturally.
- If the user reveals something about THEMSELVES (not their ideal partner), acknowledge it \
naturally — don't ignore it, but don't dwell on it either.
- Do not behave like a therapist, a clinical assessment, an interview form, or a generic chatbot.
- Keep each response short — one or two sentences, then your next question.

You're building toward a full picture across these base fields: personality, lifestyle, \
physical_type (what draws them physically), relationship_dynamic (how they want to relate \
day-to-day — conflict, independence, affection), love_language (how they give/receive care \
and affection), dealbreakers, and about_you (something real about who's asking, not just what \
they want). Track which of these the conversation has genuinely covered so far — a field only \
counts once the user has said something concrete about it, not just because you asked. Once \
the free-flowing conversation naturally covers most of these, that's fine and complete; but if \
several turns have passed and some fields are still untouched, steer your next question toward \
one of them — naturally, as a matchmaker genuinely curious about that side of things, never as \
a checklist item ("I still need to ask about X")."""

MINIMUM_USER_TURNS = 3
COMPLETION_MESSAGE = (
    "I think I'm starting to understand who you're looking for. "
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
    """history = full message list so far, INCLUDING the latest user turn.
    One structured-output call returns both the natural reply and the
    model's own judgment of which BASE_CATEGORIES are covered by the
    conversation so far (cumulative — re-derived from the full transcript
    each turn, not tracked incrementally, so there's no extra state to
    persist between turns)."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.7, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ConversationTurnResult)
    result = structured_llm.invoke(_to_langchain_messages(history))
    # Defensive: only trust category names we actually asked about — an
    # LLM inventing a slightly different label shouldn't silently make the
    # gate impossible to satisfy, so ignore anything unrecognized rather
    # than either crashing or letting it count.
    result.categories_covered = [c for c in result.categories_covered if c in BASE_CATEGORIES]
    return result


def user_turn_count(history: list[dict]) -> int:
    return sum(1 for m in history if m["role"] == "user")


def is_ready_to_complete(history: list[dict], categories_covered: list[str]) -> bool:
    """Ready once every base category has been covered AND a small minimum
    of turns have happened — the turn floor exists only so one very long
    first message can't claim full coverage before the conversation feels
    like an actual back-and-forth."""
    if user_turn_count(history) < MINIMUM_USER_TURNS:
        return False
    return set(BASE_CATEGORIES) <= set(categories_covered)
