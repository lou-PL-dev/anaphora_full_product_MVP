"""Build the clean Blueprint projection from source-preserving evidence.

Raw observations are append-only (except when a source such as one Discovery
is deliberately replaced).  The Blueprint shown to members and used by
matching is rebuilt from the full evidence set, so semantic duplicates do not
accumulate across conversations, Discoveries, and friend contributions.
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from .llm import get_chat_llm
from .models import BlueprintEvidence, BlueprintSignal, User
from .schemas import CanonicalBlueprintResult


ALLOWED_CATEGORIES = {
    "ME": {"personality", "lifestyle", "relationship_behavior", "core_values", "physical_type"},
    "IDEAL_PARTNER": {"personality", "lifestyle", "physical_type"},
    "US": {"relationship_shape", "connection_affection", "shared_direction", "boundaries"},
}

CANONICALIZATION_SYSTEM_PROMPT = """You are the canonicalization layer for Anaphora's Relationship Blueprint.

You receive ALL active source observations collected so far. Return one clean, non-repetitive, MECE Blueprint projection plus one replacement ideal-partner portrait.

The three lenses are strict:
- ME = who the member is: personality, lifestyle, relationship_behavior, core_values. physical_type is allowed only when actual self/profile data supplies it.
- IDEAL_PARTNER = the person they hope to meet: personality, lifestyle, physical_type.
- US = the relationship they want to create together: relationship_shape, connection_affection, shared_direction, boundaries.

Canonicalization rules:
1. Merge semantic duplicates across every source, even when wording differs. For example, "likes to read" and "enjoys reading" become one signal; overlapping conflict-processing paraphrases become one precise signal.
2. Split compound observations when they contain genuinely independent ideas. "Warm and smart" should support separate "Warm" and "Smart" signals. The same evidence ID may therefore support more than one result.
3. Reclassify misplaced ideas into the correct lens/category. Personality traits are not lifestyle; communication behavior is not shared activity; the member's traits never belong in IDEAL_PARTNER.
4. Keep distinct preferences, tensions, and trade-offs separate. Do not merge merely because two ideas are related.
5. Use only supplied evidence. Never invent a fact, requirement, compromise, causal link, or compatibility claim.
6. Every input evidence ID must appear in at least one output signal's evidence_ids. Put the clearest primary evidence first, then all duplicate/supporting IDs. Never output an unknown ID.
7. Labels must be concise, natural, member-facing fragments. Never say "the user" or repeat taxonomy language in a label.
8. Do not decide strength: strength is resolved deterministically from linked source evidence after your response.
9. A source beginning with user_correction is authoritative for the specific evidence IDs listed in supersedes_evidence_ids. Use the corrected meaning/wording for that concept, while retaining any independent ideas supported by a compound original observation.

The narrative is a presentation layer, not a second store of facts. Write ONE coherent replacement paragraph exclusively about the IDEAL_PARTNER, addressed directly to the member. Use only IDEAL_PARTNER evidence. Never describe the member, never say "the user", never append multiple summaries, and never claim that the person will complement the member unless that exact preference is supported. If there is no IDEAL_PARTNER evidence, return an empty narrative. Use the language of the evidence when clear."""

_STRENGTH_RANK = {
    "unknown": 0,
    "preference": 1,
    "strong_preference": 2,
    "hard_requirement": 3,
}


def _effective_strength(row: BlueprintEvidence) -> str:
    # A model inference can never manufacture a non-negotiable. Only an
    # explicit source observation or member correction may remain hard.
    if row.strength == "hard_requirement" and not row.explicit:
        return "preference"
    return row.strength or "unknown"


def ensure_evidence_backfill(db: Session, user_id: str) -> int:
    """Lazily preserve pre-canonicalization signals as raw evidence once."""
    existing = (
        db.query(BlueprintEvidence.id)
        .filter(BlueprintEvidence.user_id == user_id)
        .first()
    )
    if existing:
        return 0

    legacy_signals = (
        db.query(BlueprintSignal)
        .filter(BlueprintSignal.user_id == user_id)
        .order_by(BlueprintSignal.created_at.asc())
        .all()
    )
    for signal in legacy_signals:
        db.add(BlueprintEvidence(
            # Separate tables may safely share IDs. This also lets an edit of
            # a legacy signal find the exact evidence row after backfill.
            id=signal.id,
            user_id=user_id,
            perspective=signal.perspective,
            category=signal.category,
            label=signal.label,
            strength=signal.strength or "preference",
            source=signal.source or "legacy",
            evidence_text=signal.evidence_text,
            confidence=signal.confidence,
            explicit=True,
        ))
    db.flush()
    return len(legacy_signals)


def add_evidence(
    db: Session,
    *,
    user_id: str,
    perspective: str,
    category: str,
    label: str,
    strength: str,
    source: str,
    evidence_text: str | None = None,
    confidence: float | None = None,
    explicit: bool = True,
) -> BlueprintEvidence:
    evidence = BlueprintEvidence(
        user_id=user_id,
        perspective=perspective,
        category=category,
        label=label.strip(),
        strength=strength,
        source=source,
        evidence_text=evidence_text,
        confidence=confidence,
        explicit=explicit,
    )
    db.add(evidence)
    db.flush()
    return evidence


def canonicalize_evidence(evidence: list[BlueprintEvidence]) -> CanonicalBlueprintResult:
    """Ask the model only for semantic grouping, wording, and taxonomy."""
    payload = [
        {
            "id": row.id,
            "perspective": row.perspective,
            "category": row.category,
            "label": row.label,
            "strength": row.strength,
            "source": row.source,
            "evidence_text": row.evidence_text,
            "confidence": row.confidence,
            "explicit": row.explicit,
            "supersedes_evidence_ids": row.supersedes_evidence_ids or [],
        }
        for row in evidence
    ]
    llm = get_chat_llm(temperature=0)
    structured_llm = llm.with_structured_output(CanonicalBlueprintResult)
    return structured_llm.invoke([
        {"role": "system", "content": CANONICALIZATION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "Active Blueprint evidence:\n\n" + json.dumps(payload, ensure_ascii=False),
        },
    ])


def _materialize(
    result: CanonicalBlueprintResult,
    evidence: list[BlueprintEvidence],
) -> list[dict]:
    """Validate grounding and deterministically restore strength/provenance.

    Every KEPT signal is still fully grounded and correctly classified —
    nothing here weakens those guarantees. What changed is the failure
    granularity: one malformed draft signal (wrong category for its
    perspective, a stray evidence ID, an empty label) used to raise and
    discard the ENTIRE Blueprint rebuild, for every piece of evidence,
    every time — a single near-miss among many good signals was
    indistinguishable from total failure. Now an invalid draft is simply
    dropped, and any evidence it would have carried falls back to that
    evidence's own already-validated perspective/category (assigned when
    it was first captured) rather than being silently lost.
    """
    evidence_by_id = {row.id: row for row in evidence}
    active_ids = set(evidence_by_id)
    used_ids: set[str] = set()
    merged: dict[tuple[str, str, str], dict] = {}

    for draft in result.signals:
        perspective = draft.perspective.strip().upper()
        category = draft.category.value
        label = draft.label.strip()
        if perspective not in ALLOWED_CATEGORIES or category not in ALLOWED_CATEGORIES[perspective]:
            continue  # drop this one signal, not the whole rebuild
        if not label or "the user" in label.casefold():
            continue

        linked_ids = [eid for eid in dict.fromkeys(draft.evidence_ids) if eid in active_ids]
        if not linked_ids:
            continue  # nothing left to ground this signal in
        used_ids.update(linked_ids)

        key = (perspective, category, label.casefold())
        if key in merged:
            merged[key]["evidence_ids"] = list(dict.fromkeys(
                merged[key]["evidence_ids"] + linked_ids
            ))
        else:
            merged[key] = {
                "perspective": perspective,
                "category": category,
                "label": label,
                "evidence_ids": linked_ids,
            }

    # Evidence the model didn't fold into any valid signal still deserves a
    # place in the Blueprint — fall back to a direct 1:1 signal using that
    # evidence's own perspective/category rather than dropping what the
    # member (or a friend) actually said.
    for evidence_id in active_ids - used_ids:
        row = evidence_by_id[evidence_id]
        if row.category not in ALLOWED_CATEGORIES.get(row.perspective, set()):
            continue
        label = (row.label or "").strip()
        if not label or "the user" in label.casefold():
            continue
        key = (row.perspective, row.category, label.casefold())
        if key in merged:
            merged[key]["evidence_ids"].append(evidence_id)
        else:
            merged[key] = {
                "perspective": row.perspective,
                "category": row.category,
                "label": label,
                "evidence_ids": [evidence_id],
            }

    materialized = []
    for item in merged.values():
        linked = [evidence_by_id[evidence_id] for evidence_id in item["evidence_ids"]]
        corrections = [row for row in linked if (row.source or "").startswith("user_correction:")]
        strongest = (
            max(corrections, key=lambda row: (row.created_at, row.id))
            if corrections
            else max(
                linked,
                key=lambda row: _STRENGTH_RANK.get(_effective_strength(row), 0),
            )
        )
        primary = linked[0]
        confidences = [row.confidence for row in linked if row.confidence is not None]
        materialized.append({
            **item,
            "strength": _effective_strength(strongest),
            "evidence_text": primary.evidence_text,
            "confidence": max(confidences) if confidences else None,
        })
    return materialized


def rebuild_blueprint(db: Session, user: User) -> list[BlueprintSignal]:
    """Atomically replace the canonical projection for one member."""
    db.flush()
    evidence = (
        db.query(BlueprintEvidence)
        .filter(BlueprintEvidence.user_id == user.id)
        .order_by(BlueprintEvidence.created_at.asc(), BlueprintEvidence.id.asc())
        .all()
    )

    if evidence:
        result = canonicalize_evidence(evidence)
        projection = _materialize(result, evidence)
        # The narrative is presentation-layer only (see module docstring) —
        # a stray "the user" slipping into a paragraph of otherwise-fine
        # prose is never worth discarding a correctly-grounded projection
        # over, so fall back to no narrative rather than raising.
        narrative = result.narrative.strip()
        if "the user" in narrative.casefold():
            narrative = ""
    else:
        projection = []
        narrative = ""

    # Nothing is deleted until the new projection has passed all validation.
    db.query(BlueprintSignal).filter(
        BlueprintSignal.user_id == user.id,
    ).delete(synchronize_session=False)

    signals = []
    for item in projection:
        signal = BlueprintSignal(
            user_id=user.id,
            perspective=item["perspective"],
            category=item["category"],
            label=item["label"],
            strength=item["strength"],
            source="canonical",
            evidence_text=item["evidence_text"],
            confidence=item["confidence"],
            evidence_ids=item["evidence_ids"],
        )
        db.add(signal)
        signals.append(signal)

    user.blueprint_narrative = narrative or None
    db.add(user)
    db.flush()
    return signals


def signals_supported_by(
    signals: list[BlueprintSignal], evidence_ids: set[str]
) -> list[BlueprintSignal]:
    return [
        signal for signal in signals
        if evidence_ids.intersection(signal.evidence_ids or [])
    ]
