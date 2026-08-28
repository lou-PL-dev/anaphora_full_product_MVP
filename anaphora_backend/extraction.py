"""
Operation B — Structured extraction (PRD section 31).
Turns a completed conversation transcript into a Relationship Blueprint,
keeping ME and IDEAL_PARTNER strictly separate (section 12).
"""
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import ExtractionResult

EXTRACTION_SYSTEM_PROMPT = """You extract structured relationship-matchmaking data from a \
conversation transcript between Anaphora (an AI matchmaker) and a user.

Critical rule: NEVER confuse what the user IS with what the user WANTS. If the user says \
"I'm quite independent and need a lot of time for myself," that is a signal about the user \
themselves (perspective: ME), not a description of their ideal partner.

For each signal you extract:
- Assign it to the correct category (personality, lifestyle, relationship_dynamic, \
attraction, values, or — for the ideal partner only — dealbreakers).
- Assign a strength: "hard_requirement" only if the user explicitly describes it as \
essential/non-negotiable; "strong_preference" if they emphasize it; "preference" for \
anything mentioned without strong emphasis; "unknown" if genuinely ambiguous.
- Include a short evidence_text quote (a few words) from the transcript that justifies it.

Only extract what is actually supported by the transcript. Do not invent signals."""


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
    result = structured_llm.invoke([
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Transcript:\n\n{transcript}"},
    ])
    return result
