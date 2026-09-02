"""Ask Friends — signal extraction (PRD section 21, "Friend Signal
Processing").

Turns one friend's private answers into (a) a short paraphrased narrative
and (b) candidate structured signals, without ever quoting the friend's
raw words. Individual friend responses stay private (PRD section 18); only
this paraphrase and the resulting signals may ever reach the inviting user,
and only once they explicitly accept each signal.
"""
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import FriendExtractionResult

FRIEND_EXTRACTION_PROMPT = """You read a trusted friend's private answers about {name}, describing what kind of partner might suit {name} and how {name} shows up in relationships.

Your job:
1. Write ONE short (2-4 sentence) narrative paraphrasing what this friend perceives about {name} — third person, warm, natural. NEVER quote the friend's exact words. The friend's raw answers stay private forever; only this paraphrase and the structured signals below may ever reach {name}.
2. Extract structured observations from the answers, each tagged:
   - ME: something this reveals about {name} themselves.
   - IDEAL_PARTNER: something this reveals about who might suit {name}.
   Use ONLY these seven categories: personality, lifestyle, physical_type, relationship_dynamic, love_language, dealbreakers, values.

Rules:
- Never invent facts the answers don't support.
- evidence_text must be a short paraphrase, never a verbatim quote from the friend.
- Only use hard_requirement when the friend frames something as essential/non-negotiable. Default to preference or strong_preference.
- Keep confidence conservative — a friend's outside view is valuable but less certain than {name}'s own words.
- If an answer is too thin or generic to support a signal, skip it rather than guessing."""


def extract_friend_signals(name: str, labeled_answers: dict[str, str]) -> FriendExtractionResult:
    """labeled_answers maps each question's full (name-substituted) prompt
    text to the friend's answer, so the LLM sees real questions, not ids."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.2, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(FriendExtractionResult)
    payload = "\n\n".join(f"Q: {question}\nA: {answer}" for question, answer in labeled_answers.items())
    return structured_llm.invoke([
        {"role": "system", "content": FRIEND_EXTRACTION_PROMPT.format(name=name)},
        {"role": "user", "content": f"Friend's answers about {name}:\n\n{payload}"},
    ])
