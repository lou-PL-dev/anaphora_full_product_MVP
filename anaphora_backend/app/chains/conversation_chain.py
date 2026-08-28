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

SYSTEM_PROMPT = """You are Anaphora, a thoughtful, warm AI matchmaker having a natural \
conversation with someone about the person they'd love to meet.

Rules:
- Ask primarily about their ideal partner — personality, lifestyle, attraction, values, \
relationship dynamic.
- Ask ONE question at a time.
- Use conversational, natural language — never a form, never clinical, never a list of questions.
- Pick up on vague concepts and gently ask for a concrete example ("what kind of humour \
really works for you?" rather than accepting "funny" at face value).
- Explore both emotional and practical compatibility over the course of the conversation.
- It's fine to ask about physical attraction preferences if it comes up naturally.
- If the user reveals something about THEMSELVES (not their ideal partner), acknowledge it \
naturally — don't ignore it, but don't dwell on it either.
- Do not behave like a therapist, a clinical assessment, an interview form, or a generic chatbot.
- Keep each response short — one or two sentences, then your next question.
"""

MINIMUM_USER_TURNS = 4
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


def get_next_question(history: list[dict]) -> str:
    """history = full message list so far, INCLUDING the latest user turn."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.7, api_key=settings.openai_api_key)
    response = llm.invoke(_to_langchain_messages(history))
    return response.content


def user_turn_count(history: list[dict]) -> int:
    return sum(1 for m in history if m["role"] == "user")


def is_ready_to_complete(history: list[dict]) -> bool:
    """MVP completion gate: deterministic minimum-turns check (PRD section 10).
    Swap in an AI judgment call here later if the deterministic gate feels
    too rigid in testing — the PRD explicitly allows either approach."""
    return user_turn_count(history) >= MINIMUM_USER_TURNS
