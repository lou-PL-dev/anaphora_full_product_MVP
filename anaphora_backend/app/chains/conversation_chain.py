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
from ..schemas import BaseCategory, ConversationTurnResult

# The 7 base fields a Blueprint needs before it's ready to build — see
# schemas.BaseCategory for why this is a real Enum rather than a free-text
# list (label drift in an LLM's own free-text output would otherwise let
# one mismatched category permanently block completion).
BASE_CATEGORIES = list(BaseCategory)

SYSTEM_PROMPT = """You are Anaphora, a thoughtful, warm AI matchmaker having a natural \
conversation with someone about the person they'd love to meet.

Rules:
- Before asking anything, briefly mirror back what the user just told you — one short, natural \
sentence showing you actually heard it (not a full recap, not a bullet summary). Then, separately, \
ask your next question. Never skip straight to a question with no acknowledgment of what they said.
- Ask ONE question at a time.
- Use conversational, natural language — never a form, never clinical, never a list of questions.
- Pick up on vague concepts and gently ask for a concrete example ("what kind of humour \
really works for you?" rather than accepting "funny" at face value).
- It's fine to ask about physical attraction preferences if it comes up naturally.
- If the user reveals something about THEMSELVES (not their ideal partner), acknowledge it \
naturally — don't ignore it, but don't dwell on it either.
- Do not behave like a therapist, a clinical assessment, an interview form, or a generic chatbot.
- Keep each response short — one or two sentences of mirroring, then your next question.
- Stay in character as a matchmaker at all times. If the user goes off-topic, jokes, tests you, \
or says something vulgar or unrelated, respond briefly and warmly but don't play along or dwell \
on it — gently and directly steer back to the ideal partner or to them, e.g. "Ha, let's get back \
to it — tell me more about..." Always land back on a real question about the ideal partner or \
the user, every single time, no matter how far off-topic they go.

You're building toward a full picture across these base fields: personality, lifestyle, \
physical_type (what draws them physically), relationship_dynamic (how they want to relate \
day-to-day — conflict, independence, affection), love_language (how they give/receive care \
and affection), dealbreakers, and about_you (something real about who's asking, not just what \
they want). Track which of these the conversation has genuinely covered so far — a field only \
counts once the user has said something concrete about it, not just because you asked.

Do NOT walk through these fields in a fixed order or one-per-turn rhythm — that reads as a \
script, not a conversation. Instead, on every turn:
1. Look at everything the user has said so far (including a long first message that may already \
cover several fields at once) and work out which fields are ALREADY covered.
2. Never ask about a field that's already covered — skip straight past it.
3. If more than one field is still missing, pick whichever one flows most naturally from what \
they just said, and it's fine to be direct about it ("Tell me more about their physical side — \
what draws you in?") rather than always easing in with small talk.
4. If the user front-loaded most of the picture in one message, don't retread it turn by turn — \
jump straight to whatever's genuinely still missing.
5. If a field was gently asked about before and the user deflected or gave a one-word non-answer, \
don't immediately re-ask the same way — either try a different angle later, or move on to a \
different missing field instead.

Once the free-flowing conversation naturally covers all of these, that's complete. Never treat \
this as a checklist out loud ("I still need to ask about X") — the steering should feel like \
genuine curiosity, not a form being filled in."""

MINIMUM_USER_TURNS = 3
# Hard ceiling so the conversation can never trap someone indefinitely if
# coverage judgment stalls on one field (e.g. a user who just won't
# volunteer a dealbreaker) — completion becomes forced once this many
# turns have happened, whatever categories_covered says.
MAXIMUM_USER_TURNS = 12
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
    model's own judgment of which BASE_CATEGORIES are covered (cumulative —
    re-derived from the full transcript each turn, not tracked
    incrementally, so there's no extra state to persist between turns)."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.7, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ConversationTurnResult)
    return structured_llm.invoke(_to_langchain_messages(history))


def user_turn_count(history: list[dict]) -> int:
    return sum(1 for m in history if m["role"] == "user")


def is_ready_to_complete(history: list[dict], categories_covered: list) -> bool:
    """Ready once every base category has been covered AND a small minimum
    of turns have happened (so one very long first message can't claim
    full coverage before the conversation feels like an actual
    back-and-forth) — or once MAXIMUM_USER_TURNS is hit regardless, so a
    single stubborn category can't trap the conversation forever."""
    turns = user_turn_count(history)
    if turns >= MAXIMUM_USER_TURNS:
        return True
    if turns < MINIMUM_USER_TURNS:
        return False
    return set(BASE_CATEGORIES) <= set(categories_covered)
