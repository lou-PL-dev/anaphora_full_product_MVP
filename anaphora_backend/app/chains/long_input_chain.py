"""LLM-assisted digesting for long user messages.

A long voice/text message is still stored verbatim and remains ONE user turn.
This chain only creates compact working memory for steering and final extraction
so later model calls do not repeatedly ingest the entire raw block.
"""
from __future__ import annotations

from ..config import settings
from ..llm import get_chat_llm
from ..schemas import CoverageField, LongInputChunkDigest, ConversationObservation
from .input_segmentation import segment_long_input

LONG_INPUT_DIGEST_PROMPT = """You are processing ONE chunk of a longer user message for Anaphora.
Extract only what this chunk actually says. Do not answer the user.

Use the shared three-lens taxonomy:
- ME = who the user is: personality, lifestyle, relationship_behavior, core_values.
- IDEAL_PARTNER = who they want: personality, lifestyle, physical_type.
- US = what they want to create together: relationship_shape,
  connection_affection, shared_direction, boundaries.

For key_points, preserve meaningful nuance, qualifiers, tensions, and contradictions instead of smoothing them into generic summaries.
For observations, create atomic structured memories with perspective, category, concise normalized label, strength, confidence, explicit/inferred status, and a SHORT verbatim evidence phrase.
Write observation labels as concise member-facing fragments; never label someone as "the user".
For coverage_fields, mark only perspective-specific Blueprint fields genuinely supported by this chunk.
For evidence_snippets, retain a few SHORT verbatim phrases from the user that are particularly useful for grounding or tone.
Never infer facts that are not supported by the chunk. A cautious inference from a concrete example may be explicit=false; do not convert it into a hard requirement."""


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


def _observation_key(obs: ConversationObservation) -> tuple[str, str, str]:
    return (obs.perspective.upper(), obs.category.value, obs.label.strip().casefold())


def _dedupe_observations(values: list[ConversationObservation]) -> list[ConversationObservation]:
    seen: set[tuple[str, str, str]] = set()
    result: list[ConversationObservation] = []
    for obs in values:
        key = _observation_key(obs)
        if key not in seen:
            seen.add(key)
            result.append(obs)
    return result


def merge_chunk_digests(digests: list[LongInputChunkDigest]) -> LongInputChunkDigest:
    """Deterministically merge chunk-level understanding in source order."""
    key_points: list[str] = []
    evidence: list[str] = []
    observations: list[ConversationObservation] = []
    coverage: list[CoverageField] = []
    coverage_seen: set[CoverageField] = set()

    for digest in digests:
        key_points.extend(digest.key_points)
        evidence.extend(digest.evidence_snippets)
        observations.extend(digest.observations)
        for field in digest.coverage_fields:
            if field not in coverage_seen:
                coverage_seen.add(field)
                coverage.append(field)

    return LongInputChunkDigest(
        key_points=_dedupe_strings(key_points),
        coverage_fields=coverage,
        evidence_snippets=_dedupe_strings(evidence),
        observations=_dedupe_observations(observations),
    )


def digest_long_input(text: str) -> LongInputChunkDigest:
    """Segment and understand a long message without generating any reply."""
    chunks = segment_long_input(text)
    if not chunks:
        return LongInputChunkDigest()

    llm = get_chat_llm(settings.openai_conversation_model, temperature=0)
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
    """Compact internal representation used instead of re-sending raw long text."""
    points = "\n".join(f"- {point}" for point in digest.key_points) or "- No reliable key points extracted"
    coverage = ", ".join(field.value for field in digest.coverage_fields) or "none"
    evidence = "\n".join(f'- "{snippet}"' for snippet in digest.evidence_snippets) or "- none retained"
    observations = "\n".join(
        f"- {obs.perspective}/{obs.category.value}: {obs.label} "
        f"(strength={obs.strength.value}, confidence={obs.confidence:.2f}, explicit={obs.explicit})"
        for obs in digest.observations
    ) or "- none"
    return (
        "[Internal digest of one long user message; treat this as the user's single turn.]\n"
        f"Key points:\n{points}\n"
        f"Atomic observations:\n{observations}\n"
        f"Perspective-specific coverage: {coverage}\n"
        f"Verbatim evidence snippets:\n{evidence}"
    )
