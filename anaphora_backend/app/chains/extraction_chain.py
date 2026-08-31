"""Operation B — Structured Relationship Blueprint extraction.

Turns a conversation into two symmetric perspectives: ME and IDEAL_PARTNER.
These are the two halves later used for reciprocal matching against another
person's ME and IDEAL_PARTNER profiles.
"""
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import ExtractionResult

EXTRACTION_SYSTEM_PROMPT = """You extract structured relationship-matchmaking data from a conversation transcript between Anaphora (an AI matchmaker) and a user, AND write a short human portrait of the ideal partner from the same transcript.

The Relationship Blueprint is reciprocal. It will eventually be compared like this:
- this user's ME against another person's IDEAL_PARTNER
- another person's ME against this user's IDEAL_PARTNER
- plus mutual compatibility between both ME profiles.
Therefore ME and IDEAL_PARTNER MUST be equally precise and use the same dimensions.

Critical rule: NEVER confuse what the user IS with what the user WANTS. A sentence may legitimately produce signals on BOTH sides. Example: "I'm quite homey but want someone adventurous who gets me out sometimes" supports ME/lifestyle = home-oriented AND IDEAL_PARTNER/lifestyle = adventurous.

STRUCTURED SIGNALS (same seven categories for ideal_partner and me):
- personality
- lifestyle
- physical_type
- relationship_dynamic
- love_language
- dealbreakers
- values

Perspective-specific meaning:
- ME/physical_type = the user's own physical characteristics or presentation ONLY when voluntarily stated. IDEAL_PARTNER/physical_type = what attracts them physically.
- IDEAL_PARTNER/dealbreakers = things the user will not accept in a partner. ME/dealbreakers is NOT "things I dislike"; only capture a concrete characteristic/circumstance about the user when they explicitly present it as materially relevant to reciprocal matching. Never guess what another person would reject.
- relationship_dynamic and love_language may have complementary rather than identical fit: capture what the user says about themselves under ME and what they want from a partner under IDEAL_PARTNER.

For every signal:
- Assign the correct perspective and category.
- strength = hard_requirement only for explicit essentials/non-negotiables; strong_preference when emphasized; preference for ordinary stated preferences; unknown only when genuinely ambiguous.
- Include a short evidence_text phrase from the transcript.
- Extract only what the transcript supports. Do not fill missing categories just to make a profile look complete.
- Do not infer sensitive traits such as health, religion, political beliefs, sexuality or ethnicity unless the user explicitly states information that is necessary to preserve their own expressed matchmaking preference/context.

NARRATIVE:
- Write ONE flowing portrait of the ideal partner — several short paragraphs, not a list — the way a perceptive close friend would describe someone they think the user would love to meet.
- Weave together only supported information; be concrete without inventing facts.
- Write it in the SAME LANGUAGE the user used in the conversation."""


def _format_transcript(history: list[dict]) -> str:
    lines = []
    for m in history:
        speaker = "User" if m["role"] == "user" else "Anaphora"
        lines.append(f"{speaker}: {m['content']}")
    return "\n".join(lines)


def extract_blueprint(history: list[dict]) -> ExtractionResult:
    llm = ChatOpenAI(model=settings.openai_model, temperature=0, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ExtractionResult)

    transcript = _format_transcript(history)
    return structured_llm.invoke([
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Transcript:\n\n{transcript}"},
    ])
