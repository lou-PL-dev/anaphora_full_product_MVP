"""
Operation B — Structured extraction (PRD section 31).
Turns a completed conversation transcript into a Relationship Blueprint,
keeping ME and IDEAL_PARTNER strictly separate (section 12).
"""
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import ExtractionResult

EXTRACTION_SYSTEM_PROMPT = """You extract structured relationship-matchmaking data from a \
conversation transcript between Anaphora (an AI matchmaker) and a user, AND write a short \
human portrait of the ideal partner from the same transcript.

Critical rule: NEVER confuse what the user IS with what the user WANTS. If the user says \
"I'm quite independent and need a lot of time for myself," that is a signal about the user \
themselves (perspective: ME), not a description of their ideal partner.

Some long user turns may appear as an internal digest rather than the full raw message. Treat those digests as grounded working memory from that single user turn; use their retained verbatim evidence snippets for evidence_text and never invent details beyond the digest.

STRUCTURED SIGNALS (ideal_partner and me — same 7 categories apply to both):
- Assign each signal to the correct category: personality, lifestyle, physical_type, \
relationship_dynamic, love_language, dealbreakers, or values.
- Assign a strength: "hard_requirement" only if the user explicitly describes it as \
essential/non-negotiable; "strong_preference" if they emphasize it; "preference" for \
anything mentioned without strong emphasis; "unknown" if genuinely ambiguous.
- Include a short evidence_text quote (a few words) from the transcript that justifies it.
- Only extract what is actually supported by the transcript. Do not invent signals.

NARRATIVE:
- Write ONE flowing portrait of the ideal partner — several short paragraphs, not a list — \
the way a perceptive close friend would describe someone they think you'd love to meet, \
weaving personality, how they move through daily life, what draws you to them physically, \
how they connect with a partner, and where they plausibly are in life (work, stage of life) \
into a real, specific person, not a trait inventory. It's fine to address the user directly \
in places ("you'd bring your own two worlds together") the way a warm, opinionated friend \
would.
- Base it ONLY on what the transcript actually supports, extrapolated the way a friend who \
was really listening would — concrete and specific rather than generic, but not inventing \
facts the user never implied.
- Write it in the SAME LANGUAGE the user wrote in during the conversation."""


def _format_transcript(history: list[dict]) -> str:
    lines = []
    for m in history:
        speaker = "User" if m["role"] == "user" else "Anaphora"
        content = m.get("processing_summary") or m["content"]
        lines.append(f"{speaker}: {content}")
    return "\n".join(lines)


def extract_blueprint(history: list[dict]) -> ExtractionResult:
    llm = ChatOpenAI(model=settings.openai_model, temperature=0, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ExtractionResult)

    transcript = _format_transcript(history)
    result = structured_llm.invoke([
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Transcript:\n\n{transcript}"},
    ])
    return result
