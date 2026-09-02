"""Ask Friends — signal extraction (PRD section 21, "Friend Signal
Processing").

Turns one friend's private answers into (a) a short paraphrased narrative
and (b) candidate structured signals, without ever quoting the friend's
raw words. Individual friend responses stay private (PRD section 18); only
this paraphrase and the resulting signals may ever reach the inviting
user, and only once they explicitly accept each signal. The narrative is
shown directly to that inviting user on their own Blueprint review, so it
addresses them as "you" — there's no need to know or use anyone's name.
"""
from ..llm import get_chat_llm
from ..schemas import FriendExtractionResult

FRIEND_EXTRACTION_PROMPT = """You read a trusted friend's private answers about the person who invited them to answer — describing what kind of partner might suit that person and how they show up in relationships. You will address that person directly as "you", since they are the one who will read your output.

Your job:
1. Write ONE short (2-4 sentence) narrative paraphrasing what this friend perceives, addressed to "you" — warm, natural. NEVER quote the friend's exact words. The friend's raw answers stay private forever; only this paraphrase and the structured signals below may ever reach you.
2. Extract structured observations into the shared Blueprint:
   - ME: who the user is — personality, lifestyle, relationship_behavior, core_values.
   - IDEAL_PARTNER: who might suit them — personality, lifestyle, physical_type.
   - US: the kind of relationship that might suit them — relationship_shape,
     connection_affection, shared_direction, boundaries.

Rules:
- Never invent facts the answers don't support.
- evidence_text must be a short paraphrase, never a verbatim quote from the friend.
- Only use hard_requirement when the friend frames something as essential/non-negotiable. Default to preference or strong_preference.
- Keep confidence conservative — a friend's outside view is valuable but less certain than your own words.
- If an answer is too thin or generic to support a signal, skip it rather than guessing."""


def extract_friend_signals(labeled_answers: dict[str, str]) -> FriendExtractionResult:
    """labeled_answers maps each question's full prompt text to the
    friend's answer, so the LLM sees real questions, not ids."""
    llm = get_chat_llm(temperature=0.2)
    structured_llm = llm.with_structured_output(FriendExtractionResult)
    payload = "\n\n".join(f"Q: {question}\nA: {answer}" for question, answer in labeled_answers.items())
    return structured_llm.invoke([
        {"role": "system", "content": FRIEND_EXTRACTION_PROMPT},
        {"role": "user", "content": f"Friend's answers:\n\n{payload}"},
    ])
