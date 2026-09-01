"""Utilities for resilient handling of long conversation messages.

This module deliberately does NOT impose a user-facing length limit. The raw
message remains the source evidence; segmentation is only an internal tool so
later extraction/steering steps can process a long voice transcript in bounded,
meaningful pieces instead of forcing one model call to digest an arbitrarily
large block.

The splitter is deterministic and network-free so it can be tested cheaply.
It prefers paragraph boundaries, then sentence boundaries, and only falls back
to a hard character window for a single unusually long sentence/transcript
segment.
"""
from __future__ import annotations

import re

# Character counts are intentionally used rather than a tokenizer dependency.
# They are not presented as model token limits; they are internal processing
# thresholds that can be tuned independently from the UX.
LONG_INPUT_THRESHOLD_CHARS = 8_000
TARGET_CHUNK_CHARS = 4_000
MAX_CHUNK_CHARS = 5_500

_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")
_PARAGRAPH_BOUNDARY_RE = re.compile(r"\n\s*\n+")


def is_long_input(text: str) -> bool:
    """Whether a message would benefit from internal segmented processing."""
    return len((text or "").strip()) > LONG_INPUT_THRESHOLD_CHARS


def _hard_split(text: str, max_chars: int) -> list[str]:
    """Last-resort splitter for one span with no usable sentence boundaries.

    Prefer breaking on whitespace near max_chars; only cut mid-word if the
    input itself contains no suitable whitespace (e.g. malformed transcript).
    """
    parts: list[str] = []
    remaining = text.strip()
    while len(remaining) > max_chars:
        cut = remaining.rfind(" ", 0, max_chars + 1)
        if cut < max_chars // 2:
            cut = max_chars
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def _sentence_units(paragraph: str, max_chars: int) -> list[str]:
    paragraph = paragraph.strip()
    if not paragraph:
        return []
    if len(paragraph) <= max_chars:
        return [paragraph]

    sentences = [s.strip() for s in _SENTENCE_BOUNDARY_RE.split(paragraph) if s.strip()]
    if len(sentences) <= 1:
        return _hard_split(paragraph, max_chars)

    units: list[str] = []
    for sentence in sentences:
        if len(sentence) <= max_chars:
            units.append(sentence)
        else:
            units.extend(_hard_split(sentence, max_chars))
    return units


def segment_long_input(
    text: str,
    target_chars: int = TARGET_CHUNK_CHARS,
    max_chars: int = MAX_CHUNK_CHARS,
) -> list[str]:
    """Split one user message into ordered, bounded internal processing chunks.

    The returned chunks preserve all non-whitespace content in order. They are
    *not* conversation turns and should never cause multiple user-visible AI
    replies. For short input this simply returns ``[text.strip()]``.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    paragraphs = [p.strip() for p in _PARAGRAPH_BOUNDARY_RE.split(cleaned) if p.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        units.extend(_sentence_units(paragraph, max_chars))

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for unit in units:
        separator_len = 2 if current else 0
        proposed_len = current_len + separator_len + len(unit)

        if current and proposed_len > target_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
            separator_len = 0

        # A unit produced by _sentence_units is <= max_chars, so it can stand
        # alone safely even when it is larger than target_chars.
        current.append(unit)
        current_len += separator_len + len(unit)

    if current:
        chunks.append("\n\n".join(current))

    return chunks
