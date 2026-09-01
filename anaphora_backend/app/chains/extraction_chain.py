"""
Operation B — Structured Blueprint reconciliation.

The canonical machine-readable source is the accumulated atomic observations
captured during conversation. The polished narrative is generated from that
state; it is not itself the source of truth for matching.
"""
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import ConversationObservation, ExtractionResult

RECONCILIATION_SYSTEM_PROMPT = """You reconcile Anaphora's accumulated atomic conversation observations into one Relationship Blueprint.

Critical rules:
- Treat the observations as the canonical machine-readable evidence.
- Keep ME and IDEAL_PARTNER strictly separate.
- Preserve meaningful tensions or apparently contradictory needs as separate signals when both are supported; do not smooth them into a vague compromise.
- Deduplicate observations that clearly mean the same thing, preferring the more explicit and better-supported wording.
- Never upgrade an inferred observation into a hard_requirement.
- hard_requirement is allowed only for explicit evidence that clearly says essential/non-negotiable/dealbreaker.
- Keep confidence conservative. Do not invent missing facts.
- evidence_text must remain a short phrase grounded in the supplied evidence.

Return the same seven categories for both perspectives: personality, lifestyle, physical_type, relationship_dynamic, love_language, dealbreakers, values.

After reconciling the structured signals, write ONE flowing human-readable portrait of the IDEAL_PARTNER. The narrative is only a presentation layer over the structured evidence. It must not add facts, erase tensions, or become more authoritative than the signals. Write it in the same language as the supplied evidence where that is clear."""


def observations_from_history(history: list[dict]) -> list[ConversationObservation]:
    """Collect canonical observations stored on user turns, preserving order."""
    observations: list[ConversationObservation] = []
    for message in history:
        if message.get("role") != "user":
            continue
        for raw in message.get("observations") or []:
            observations.append(ConversationObservation.model_validate(raw))
    return observations


def reconcile_blueprint(observations: list[ConversationObservation]) -> ExtractionResult:
    """Build the canonical Blueprint and narrative from accumulated evidence."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(ExtractionResult)
    payload = "\n".join(
        f"{i + 1}. perspective={obs.perspective}; category={obs.category.value}; "
        f"label={obs.label}; strength={obs.strength.value}; confidence={obs.confidence:.2f}; "
        f"explicit={obs.explicit}; evidence={obs.evidence_text or '(none)'}"
        for i, obs in enumerate(observations)
    )
    return structured_llm.invoke([
        {"role": "system", "content": RECONCILIATION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Accumulated observations:\n\n{payload or '(none)'}"},
    ])


def extract_blueprint(history: list[dict]) -> ExtractionResult:
    """Compatibility entry point: reconcile from stored observations.

    Iteration 2 intentionally stops re-reading the entire raw transcript at
    completion. Raw messages remain stored for traceability, but structured
    observations drive the canonical Blueprint.
    """
    observations = observations_from_history(history)
    return reconcile_blueprint(observations)
