"""Generate synthetic candidates with BOTH sides of the Anaphora Blueprint.

A reciprocal candidate contains:
- ME: who the candidate is
- IDEAL_PARTNER: who the candidate would like to meet

The existing candidate self-narrative remains the display narrative. Both sets
of structured signals are stored in Candidate.signals so Iteration 4 matching
can evaluate USER IDEAL -> CANDIDATE ME and CANDIDATE IDEAL -> USER ME.
"""
from __future__ import annotations

import random

from generate_personas import generate_candidate_persona, generate_persona
from profiles import Persona


def generate_reciprocal_candidate_persona(
    rng: random.Random,
    candidate_id: str,
    use_llm: bool = True,
) -> Persona:
    """Create one symmetric synthetic candidate without conflating perspectives."""
    self_profile = generate_candidate_persona(rng, candidate_id, use_llm=use_llm)
    ideal_profile = generate_persona(rng, f"{candidate_id}-ideal", use_llm=use_llm)

    ideal_signals = [
        signal for signal in ideal_profile.signals
        if signal.perspective in {"IDEAL_PARTNER", "US"}
    ]
    return Persona(
        id=candidate_id,
        narrative=self_profile.narrative,
        signals=list(self_profile.signals) + ideal_signals,
    )


def candidate_me_embedding_text(persona: Persona) -> str:
    """Broad retrieval indexes who the candidate IS, never who they want."""
    me_labels = [signal.label for signal in persona.signals if signal.perspective == "ME"]
    return persona.narrative + " " + " ".join(me_labels)
