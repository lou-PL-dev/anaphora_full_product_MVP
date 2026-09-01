"""LLM-assisted digesting for long user messages.

A long voice/text message is still stored verbatim and remains ONE user turn.
This chain only creates compact working memory for steering and final extraction
so later model calls do not repeatedly ingest the entire raw block.
"""
from __future__ import annotations

from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import CoverageField, LongInputChunkDigest
from .input_segmentation import segment_long_input

LONG_INPUT_DIGEST_PROMPT = """You are processing ONE chunk of a longer user message for Anaphora.
Extract only what this chunk actually says. Do not answer the user.

Keep ME and IDEAL_PARTNER separate:
- IDEAL_PARTNER = what the user wants in another person.
- ME = what the user reveals about themselves.

For key_points, preserve meaningful nuance, qualifiers, tensions, and contradictions instead of smoothing them into generic summaries.
For coverage_fields, mark only perspective-specific Blueprint fields genuinely supported by this chunk.
For evidence_snippets, retain a few SHORT verbatim phrases from the user that are particularly useful for grounding or tone.
Never infer facts that are not supported by the chunk."""


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = (value or "").strip()
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def merge_chunk_digests(digests: list[LongInputChunkDigest]) -> LongInputChunkDigest:
    """Deterministically merge chunk-level understanding in source order."""
    key_points: list[str] = []
    evidence: list[str] = []
    coverage: list[CoverageField] = []
    coverage_seen: set[CoverageField] = set()

    for digest in digests:
        key_points.extend(digest.key_points)
        evidence.extend(digest.evidence_snippets)
        for field in digest.coverage_fields:
            if field not in coverage_seen:
                coverage_seen.add(field)
                coverage.append(field)

    return LongInputChunkDigest(
        key_points=_dedupe_strings(key_points),
        coverage_fields=coverage,
        evidence_snippets=_dedupe_strings(evidence),
    )


def digest_long_input(text: str) -> LongInputChunkDigest:
    """Segment and understand a long message without generating any reply."""
    chunks = segment_long_input(text)
    if not chunks:
        return LongInputChunkDigest()

    llm = ChatOpenAI(model=settings.openai_conversation_model, temperature=0, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(LongInputChunkDigest)
    digests = [
        structured_llm.invoke([
            {"role": "system", "content": LONG_INPUT_DIGEST_PROMPT},
            {"role": "user", "content": chunk},
        ])
        for chunk in chunks
    ]
    return merge_chunk_digests(digests)


def format_processing_summary(digest: LongInputChunkDigest) -> str:
    """Compact internal representation used instead of re-sending raw long text.

    This text is never shown to the user and never replaces the stored raw
    message. Evidence snippets remain verbatim so downstream extraction still
    has grounded wording available.
    """
    points = "\n".join(f"- {point}" for point in digest.key_points) or "- No reliable key points extracted"
    coverage = ", ".join(field.value for field in digest.coverage_fields) or "none"
    evidence = "\n".join(f'- "{snippet}"' for snippet in digest.evidence_snippets) or "- none retained"
    return (
        "[Internal digest of one long user message; treat this as the user's single turn.]\n"
        f"Key points:\n{points}\n"
        f"Perspective-specific coverage: {coverage}\n"
        f"Verbatim evidence snippets:\n{evidence}"
    )
