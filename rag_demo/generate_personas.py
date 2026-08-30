"""
rag_demo — trait-grounded persona generator.

Replaces profiles.py's uniform-random label sampling with:
  (a) a trait profile sampled from real published co-occurrence structure
      (trait_distributions.py) — this describes the IDEAL PARTNER the
      synthetic persona is going to say they're looking for, matching how
      Anaphora's own Blueprint works (a user describes who THEY want, not
      themselves);
  (b) an LLM asked to write that description as a natural first-person
      narrative, its tone/register nudged by a few originally-written style
      examples (STYLE_SEED_EXAMPLES below) rather than left to sound like
      generic LLM output;
  (c) that narrative run through anaphora_backend's OWN extraction chain
      (the exact code real conversations go through), so the resulting
      signal pool is built the same way real user data would be — this
      script does not reimplement or approximate extraction.

Output Persona/Signal shape is identical to profiles.py's, so
retrieve_similar() and every other downstream consumer work on a pool from
either generator without caring which one produced it.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from profiles import Persona, Signal, build_index, retrieve_similar
from trait_distributions import ATTACHMENT_STYLES, BIG_FIVE_TRAITS, sample_trait_profile

# anaphora_backend has no __init__.py files (plain namespace packages) —
# this only needs to be importable, not installed, so put it on sys.path.
_BACKEND_DIR = Path(__file__).resolve().parent.parent / "anaphora_backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Mirrors anaphora_backend/app/routers/conversation_router.py::OPENING_PROMPT.
# Duplicated as a plain string (rather than importing the router module)
# to avoid pulling in that module's FastAPI/DB dependencies just for one
# constant.
OPENING_PROMPT = "Tell me about the person you'd love to meet."

# --- style seeding (see dataset strategy part 2) ---------------------------
# These are ORIGINALLY WRITTEN for this demo — not excerpts from OkCupid,
# PersonalityCafe, or any other real dataset. No real person's text is
# reproduced or stored anywhere in this repo. They exist only to nudge the
# LLM's REGISTER (casual, specific, a little imperfect) away from the
# generically polished voice pure LLM generation tends toward at scale —
# the prompt explicitly tells the model to match the STYLE, not the content.
STYLE_SEED_EXAMPLES = [
    "honestly? someone who still texts back even when the conversation's "
    "kind of boring. that's it. that's the whole ask.",
    "I want someone who'll argue with me about the right way to load a "
    "dishwasher and then bring me coffee the next morning anyway.",
    "not looking for perfect, looking for someone who notices when I go "
    "quiet and actually asks about it instead of scrolling past it.",
    "someone who's excited about their own weird little hobby, whatever it "
    "is. that energy is the whole thing for me.",
]

# Every phrase below is written so "who is <phrase>" reads grammatically —
# adjectival/predicate form, not a leading verb — since offline_narrative()
# joins them that way.
BIG_FIVE_DESCRIPTIONS = {
    ("openness", "high"): "always up for trying new things and new ideas",
    ("openness", "medium"): "open to new things without needing constant novelty",
    ("openness", "low"): "someone who prefers the tried-and-true over novelty for its own sake",
    ("conscientiousness", "high"): "highly organized and serious about commitments",
    ("conscientiousness", "medium"): "reasonably organized without being rigid about it",
    ("conscientiousness", "low"): "spontaneous, not big on rigid planning",
    ("extraversion", "high"): "energized by people and drawn to social situations",
    ("extraversion", "medium"): "comfortable both socially and alone",
    ("extraversion", "low"): "introverted, recharges by being alone",
    ("agreeableness", "high"): "warm and accommodating, avoids unnecessary conflict",
    ("agreeableness", "medium"): "generally cooperative but has firm limits",
    ("agreeableness", "low"): "blunt and direct, doesn't shy from disagreement",
    ("neuroticism", "high"): "emotionally reactive, feels things intensely",
    ("neuroticism", "medium"): "generally stable with occasional stress",
    ("neuroticism", "low"): "even-keeled, rarely rattled",
}

ATTACHMENT_DESCRIPTIONS = {
    "secure": "comfortable with both closeness and independence in a relationship",
    "anxious": "someone who craves closeness and reassurance, and worries about being let down",
    "avoidant": "someone who values independence strongly and gets uneasy if things get too close too fast",
    "fearful_avoidant": "someone who wants real closeness but is wary of getting hurt by it",
}


def describe_trait_profile(trait_profile: dict) -> str:
    bf = trait_profile["big_five"]
    phrases = [BIG_FIVE_DESCRIPTIONS[(t, bf[t])] for t in BIG_FIVE_TRAITS]
    attach = ATTACHMENT_DESCRIPTIONS[trait_profile["attachment_style"]]
    return "; ".join(phrases) + f". In relationships, they are {attach}."


def build_narrative_prompt(trait_profile: dict, style_examples: list[str]) -> list[dict]:
    """Chat messages for the narrative-writing call. The trait sketch sets
    WHAT to describe (the ideal partner's traits); the style examples set
    HOW to say it (register only — the model is told explicitly not to
    reuse their wording or content)."""
    examples_block = "\n".join(f'- "{ex}"' for ex in style_examples)
    system = (
        "You write short, natural first-person messages for a synthetic test "
        "dataset, as if a user were describing the partner they'd love to meet "
        "to a matchmaking app. Write ONE paragraph (3-5 sentences), casual and "
        "specific, never a list, never clinical or like a personality-test "
        "report — a real person talking, not a psychology summary.\n\n"
        "Match the REGISTER of these examples (tone, specificity, imperfection) "
        "— do NOT reuse their wording, topics, or details, they're style "
        "reference only:\n" + examples_block
    )
    user = (
        "Write that message for someone whose ideal partner would be described "
        "this way: " + describe_trait_profile(trait_profile) + "\n\n"
        "Translate those traits into ordinary, concrete language and specific "
        "little details — never name a trait directly (no 'high conscientiousness', "
        "no 'secure attachment'). End with one brief, natural sentence revealing "
        "something small about the speaker themselves, the way people naturally "
        "do when describing what they want."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_narrative_via_llm(trait_profile: dict) -> str:
    from app.config import settings
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model=settings.openai_model, temperature=0.9, api_key=settings.openai_api_key)
    messages = build_narrative_prompt(trait_profile, STYLE_SEED_EXAMPLES)
    return llm.invoke(messages).content.strip()


def offline_narrative(trait_profile: dict) -> str:
    """Deterministic, no-LLM, no-network stand-in narrative — used by tests
    and by generate_persona(use_llm=False) so the rest of the pipeline is
    exercisable without an API key. Clearly templated on purpose: this is a
    dev/test fallback, not a claim of what a real generated persona reads
    like (see generate_narrative_via_llm for the real path)."""
    bf = trait_profile["big_five"]
    phrases = [BIG_FIVE_DESCRIPTIONS[(t, bf[t])] for t in BIG_FIVE_TRAITS]
    attach = ATTACHMENT_DESCRIPTIONS[trait_profile["attachment_style"]]
    return (
        "I'm looking for someone who is " + ", who is ".join(phrases) + ". "
        f"In relationships I want someone who is {attach}. "
        "As for me, I tend to take a while to open up to someone new."
    )


# Maps an ExtractionResult (anaphora_backend/app/schemas.py) into the flat
# Signal list profiles.py uses — the SAME (perspective, category) mapping
# anaphora_backend/app/routers/conversation_router.py::complete_conversation
# applies when storing a real conversation's extraction.
_IDEAL_PARTNER_CATEGORIES = ["personality", "lifestyle", "relationship_dynamic", "attraction", "values", "dealbreakers"]
_ME_CATEGORIES = ["personality", "lifestyle", "relationship_style", "values"]


def extraction_result_to_signals(result) -> list[Signal]:
    signals: list[Signal] = []
    for category in _IDEAL_PARTNER_CATEGORIES:
        for item in getattr(result.ideal_partner, category):
            signals.append(Signal("IDEAL_PARTNER", category, item.label, item.strength.value, item.evidence_text))
    for category in _ME_CATEGORIES:
        for item in getattr(result.me, category):
            signals.append(Signal("ME", category, item.label, item.strength.value, item.evidence_text))
    return signals


def generate_persona(rng: random.Random, persona_id: str, use_llm: bool = True) -> Persona:
    from app.chains.extraction_chain import extract_blueprint

    trait_profile = sample_trait_profile(rng)
    narrative = generate_narrative_via_llm(trait_profile) if use_llm else offline_narrative(trait_profile)
    history = [
        {"role": "assistant", "content": OPENING_PROMPT},
        {"role": "user", "content": narrative},
    ]
    result = extract_blueprint(history)
    return Persona(id=persona_id, narrative=narrative, signals=extraction_result_to_signals(result))


def generate_persona_pool(n: int, seed: int | None = None, use_llm: bool = True) -> list[Persona]:
    rng = random.Random(seed)
    return [generate_persona(rng, f"trait-grounded-{i}", use_llm=use_llm) for i in range(n)]


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", type=int, default=20, help="pool size")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "generated_personas.json")
    parser.add_argument("--offline", action="store_true", help="use the templated narrative, skip the LLM call for it (extraction still calls the LLM)")
    args = parser.parse_args()

    pool = generate_persona_pool(args.n, seed=args.seed, use_llm=not args.offline)
    args.out.write_text(json.dumps([{"id": p.id, "narrative": p.narrative, "signals": p.signal_dicts()} for p in pool], indent=2))
    print(f"Wrote {len(pool)} personas to {args.out}")

    index = build_index(pool)
    query = "I want someone who is warm, family-oriented, and loves quiet evenings at home."
    print(f"\nTop matches for: {query!r}")
    for persona, score in retrieve_similar(query, index, k=3):
        print(f"  {score:.3f}  {persona.id}")


if __name__ == "__main__":
    _main()
