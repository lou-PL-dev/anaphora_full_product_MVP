"""
Operation B — Structured Blueprint reconciliation.

The canonical machine-readable source is the accumulated atomic observations
captured during conversation. The polished narrative is generated from that
state; it is not itself the source of truth for matching.
"""
from ..llm import get_chat_llm
from ..schemas import ConversationObservation, ExtractionResult

RECONCILIATION_SYSTEM_PROMPT = """You reconcile Anaphora's accumulated atomic conversation observations into one ME / IDEAL_PARTNER / US Relationship Blueprint.

Critical rules:
- Treat the observations as the canonical machine-readable evidence.
- Keep the three lenses strictly separate: ME is who the user is, IDEAL_PARTNER is who they want, and US is the relationship they want to create.
- Preserve meaningful tensions or apparently contradictory needs as separate signals when both are supported; do not smooth them into a vague compromise.
- Deduplicate observations that clearly mean the same thing, preferring the more explicit and better-supported wording.
- Never upgrade an inferred observation into a hard_requirement.
- hard_requirement is allowed only for explicit evidence that clearly says essential/non-negotiable/dealbreaker.
- Keep confidence conservative. Do not invent missing facts.
- evidence_text must remain a short phrase grounded in the supplied evidence.

Return only the categories belonging to each lens:
- ME: personality, lifestyle, relationship_behavior, core_values, plus physical_type only when an actual self-description or profile data supports it (never ask the user for it in conversation).
- IDEAL_PARTNER: personality, lifestyle, physical_type.
- US: relationship_shape, connection_affection, shared_direction, boundaries.

After reconciling the structured signals, write ONE flowing human-readable portrait covering who the user is, who they seek, and what they hope to build together. The narrative is only a presentation layer over the structured evidence. It must not add facts, erase tensions, or become more authoritative than the signals. Write it in the same language as the supplied evidence where that is clear."""

LEGACY_TRANSCRIPT_PROMPT = """This is a legacy Anaphora conversation created before atomic observations were stored. Extract a structured Relationship Blueprint from the transcript so the user can finish their existing conversation.

Use the ME / IDEAL_PARTNER / US taxonomy. ME contains personality, lifestyle, relationship_behavior, core_values, and optional self physical_type when explicitly supplied. IDEAL_PARTNER contains personality, lifestyle and physical_type. US contains relationship_shape, connection_affection, shared_direction and boundaries. Use only supported facts, preserve tensions instead of smoothing them away, assign hard_requirement only when explicitly non-negotiable, keep confidence conservative, and retain short evidence phrases. Then write a human-readable portrait as a presentation layer over those signals."""


def observations_from_history(history: list[dict]) -> list[ConversationObservation]:
    """Collect canonical observations stored on user turns, preserving order."""
    observations: list[ConversationObservation] = []
    for message in history:
        if message.get("role") != "user":
            continue
        for raw in message.get("observations") or []:
            normalized = dict(raw)
            legacy_key = (normalized.get("perspective"), normalized.get("category"))
            legacy_map = {
                ("ME", "relationship_dynamic"): ("ME", "relationship_behavior"),
                ("ME", "love_language"): ("ME", "relationship_behavior"),
                ("ME", "values"): ("ME", "core_values"),
                ("ME", "dealbreakers"): ("US", "boundaries"),
                ("ME", "physical_type"): ("IDEAL_PARTNER", "physical_type"),
                ("IDEAL_PARTNER", "relationship_dynamic"): ("US", "relationship_shape"),
                ("IDEAL_PARTNER", "love_language"): ("US", "connection_affection"),
                ("IDEAL_PARTNER", "values"): ("US", "shared_direction"),
                ("IDEAL_PARTNER", "dealbreakers"): ("US", "boundaries"),
            }
            if legacy_key in legacy_map:
                normalized["perspective"], normalized["category"] = legacy_map[legacy_key]
            observations.append(ConversationObservation.model_validate(normalized))
    return observations


def reconcile_blueprint(observations: list[ConversationObservation]) -> ExtractionResult:
    """Build the canonical Blueprint and narrative from accumulated evidence."""
    llm = get_chat_llm(temperature=0)
    structured_llm = llm.with_structured_output(ExtractionResult)
    payload = "\n".join(
        f"{i + 1}. perspective={obs.perspective}; category={obs.category.value}; "
        f"label={obs.label}; strength={obs.strength.value}; confidence={obs.confidence:.2f}; "
        f"explicit={obs.explicit}; evidence={obs.evidence_text or '(none)'}"
        for i, obs in enumerate(observations)
    )
    return structured_llm.invoke([
        {"role": "system", "content": RECONCILIATION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Accumulated observations:\n\n{payload}"},
    ])


def _legacy_extract(history: list[dict]) -> ExtractionResult:
    """Backward compatibility only for conversations predating Iteration 2."""
    lines = []
    for message in history:
        speaker = "User" if message.get("role") == "user" else "Anaphora"
        content = message.get("processing_summary") or message.get("content", "")
        lines.append(f"{speaker}: {content}")
    transcript = "\n".join(lines)

    llm = get_chat_llm(temperature=0)
    structured_llm = llm.with_structured_output(ExtractionResult)
    return structured_llm.invoke([
        {"role": "system", "content": LEGACY_TRANSCRIPT_PROMPT},
        {"role": "user", "content": f"Transcript:\n\n{transcript}"},
    ])


def extract_blueprint(history: list[dict]) -> ExtractionResult:
    """Reconcile from canonical observations; fall back only for legacy data."""
    observations = observations_from_history(history)
    if observations:
        return reconcile_blueprint(observations)
    return _legacy_extract(history)
