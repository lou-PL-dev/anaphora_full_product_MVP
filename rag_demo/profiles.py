"""
rag_demo — baseline synthetic persona generator + retrieval demo.

This is the ORIGINAL, simple version of the persona pool: every Blueprint
signal is sampled uniformly at random from a fixed candidate pool, with no
regard for which traits actually tend to co-occur in real people (a
"warm, family-oriented homebody" and an "adrenaline-seeking, avoids
commitment" signal are exactly as likely to land in the same persona as
any other pair). That's fine for exercising the retrieval mechanics below,
but it means the pool is not realistic enough to test extraction quality
or matching behavior against — see generate_personas.py, which replaces
this sampling step with trait-distribution-grounded generation while
keeping the exact same Persona/signal shape so retrieve_similar() and
every downstream consumer don't need to know which generator produced the
pool.

Signal shape mirrors anaphora_backend/app/schemas.py (SignalItem, Strength)
and anaphora_backend/app/models.py (BlueprintSignal: perspective/category/
label/strength/evidence_text) — kept in sync by hand rather than imported,
since this baseline generator has no dependency on anaphora_backend at all
(generate_personas.py is the one that imports the real extraction chain).
"""
from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field

STRENGTHS = ["hard_requirement", "strong_preference", "preference", "unknown"]

# (perspective, category) -> candidate labels. Perspective/category pairs
# match the real Anaphora Blueprint groups (frontend GROUP_DEFS / backend
# BlueprintSignal.category) so a generated pool looks exactly like a real
# extracted one. Every label here is originally written for this demo, not
# copied from any real dataset or real user.
CANDIDATE_LABELS: dict[tuple[str, str], list[str]] = {
    ("IDEAL_PARTNER", "personality"): [
        "Warm in small, ordinary ways", "Self-deprecating sense of humour",
        "Genuinely curious about people", "Calm under pressure",
        "Emotionally expressive", "Quietly confident", "Playful and a little silly",
        "Thoughtful, slow to open up", "Dry humour and occasionally blunt",
        "Independent without disappearing", "Comfortable with silence",
        "Opinionated but genuinely open to changing their mind",
        "Creative and somewhat chaotic", "Reliable rather than spontaneous",
        "Socially bold but emotionally private", "Gentle without avoiding difficult truths",
    ],
    ("IDEAL_PARTNER", "lifestyle"): [
        "Weekends outdoors, not out late", "Settled in or near a city",
        "Loves to cook at home", "Travels often", "Early riser",
        "Homebody who loves a slow Sunday", "Active — runs or climbs regularly",
        "Prefers a small circle of close friends", "Regularly goes to live music",
        "Keeps unconventional working hours", "Very involved with family",
        "Enjoys crowded dinners and a busy social calendar", "Protects plenty of alone time",
        "Builds life around creative projects", "Likes routines with occasional impulsive trips",
        "Prefers countryside life to the centre of a city",
    ],
    ("IDEAL_PARTNER", "physical_type"): [
        "An easy laugh, expressive eyes", "Well-groomed and put together",
        "Athletic build", "Soft-spoken voice", "Confident posture",
        "Dresses with personality", "Warm smile that reaches the eyes",
        "Solid, broad build", "Soft, relaxed build", "Distinctive rather than conventionally polished",
        "Dark hair and facial hair", "Short, expressive haircut", "A slightly alternative style",
        "Elegant understated clothes", "Visible tattoos or jewellery",
    ],
    ("US", "connection_affection"): [
        "Shows love through small daily gestures", "Words of affirmation matter to them",
        "Physical affection — always in reach for a hug", "Acts of service — just does the thing",
        "Quality time over gifts", "Remembers the little things you mentioned once",
        "Checks in directly instead of expecting mind-reading", "Needs affection but not constant contact",
        "Uses humour to reconnect after tension", "Prefers practical support to emotional speeches",
        "Takes time to process before talking", "Says difficult things kindly",
        "Enjoys a lot of touch in private", "Keeps affection subtle in public",
    ],
    ("US", "shared_direction"): [
        "Family matters to them", "Honest, even when it costs something",
        "Cares about the environment", "Ambitious about their career",
        "Generous with time and money", "Politically engaged",
        "Faith is important to them", "Values personal growth",
        "Wants children and an involved family life", "Does not picture parenthood",
        "Prioritises geographic freedom", "Wants to build a stable home base",
        "Makes room for creative ambition", "Prefers enough over constant career growth",
        "Values community more than status", "Wants finances discussed openly",
    ],
    ("US", "boundaries"): [
        "Not looking for something casual", "Doesn't want kids",
        "Must be a non-smoker", "Can't be actively dating other people",
        "No history of dishonesty about big things", "Must want to live locally",
        "Won't relocate away from family", "Can't compromise on wanting kids",
        "Needs alone time, non-negotiably", "Doesn't want to merge every friendship and hobby",
        "Needs direct repair after conflict", "Cannot live with heavy drinking or regular drug use",
        "Doesn't want a relationship organised around work", "Needs financial responsibility",
        "Will not accept contempt or shouting during conflict", "Needs freedom to travel independently",
    ],
    ("ME", "personality"): [
        "Thoughtful, slow to open up", "Quick to laugh", "Introverted, needs recharge time",
        "Direct and a little blunt", "Anxious in new social settings",
        "Steady and even-keeled", "Enthusiastic and prone to overcommitting",
        "Curious but easily distracted", "Warm in person, inconsistent over text",
        "Highly organised and uncomfortable with sudden change",
    ],
    ("ME", "lifestyle"): [
        "Quiet evenings, long weekends outside", "Works long hours most weeks",
        "Recently moved to a new city", "Big on routine",
        "Splits time between two cities", "Very close with family nearby",
        "Social weeknights and quiet Sundays", "Keeps irregular creative working hours",
        "Trains several times a week", "Spends free time around live music",
        "Volunteers in the local community", "Prefers spontaneous plans",
        "Protects slow mornings", "Travels often for work",
    ],
    ("ME", "physical_type"): [
        "Warm, expressive face", "Athletic build", "Soft-spoken voice",
        "Dresses with intention", "Confident posture", "Distinctive personal style",
    ],
    ("ME", "relationship_behavior"): [
        "Needs depth early on", "Takes things slow", "Direct about needs",
        "Prone to overthinking a new relationship", "Values a lot of independence",
        "Shows care through acts of service", "Needs words of affirmation to feel secure",
        "Physical touch is how they connect", "Quality time matters more than gifts",
        "Shows love by remembering small details", "Needs time alone before resolving conflict",
        "Can become defensive before calming down", "Checks in frequently when attached",
        "Finds vulnerability easier through humour", "Avoids texting all day",
        "Apologises quickly but needs specifics", "Struggles to ask for help",
        "Makes plans and follows through",
    ],
    ("US", "relationship_shape"): [
        "Real conversation over small talk", "Comfortable with independence",
        "An equal partnership", "Gives each other space",
        "Handles conflict by talking it through", "Plans a future together early",
        "Keeps separate interests as well as shared ones", "Spends several nights together without merging homes quickly",
        "Makes major decisions collaboratively", "Prefers a relationship with clear commitment",
        "Likes spontaneity more than fixed couple routines", "Needs dependable weekly quality time",
        "Moves slowly before defining the relationship", "Shares domestic work explicitly",
    ],
    ("ME", "core_values"): [
        "Personal growth", "Financial stability", "Creative expression",
        "Community and friendship", "Career ambition", "Spiritual practice",
        "Reliability", "Intellectual curiosity", "Environmental responsibility",
        "Family loyalty", "Personal freedom", "Public service",
        "Humour during difficult moments", "A calm home life",
    ],
}

_WORD_RE = re.compile(r"[a-z0-9']+")


@dataclass
class Signal:
    perspective: str
    category: str
    label: str
    strength: str
    evidence_text: str | None = None

    def as_dict(self) -> dict:
        return {
            "perspective": self.perspective, "category": self.category,
            "label": self.label, "strength": self.strength, "evidence_text": self.evidence_text,
        }


@dataclass
class Persona:
    id: str
    narrative: str
    signals: list[Signal] = field(default_factory=list)

    def signal_dicts(self) -> list[dict]:
        return [s.as_dict() for s in self.signals]


def generate_random_profile(rng: random.Random, persona_id: str) -> Persona:
    """Uniform-random baseline: 1-3 labels per category, no correlation
    between them whatsoever — a persona can (and will) end up wanting a
    homebody AND an inveterate traveller in the same breath."""
    signals: list[Signal] = []
    for (perspective, category), pool in CANDIDATE_LABELS.items():
        count = rng.randint(1, min(3, len(pool)))
        for label in rng.sample(pool, count):
            signals.append(Signal(perspective, category, label, rng.choice(STRENGTHS)))

    ideal_bits = [s.label.lower() for s in signals if s.perspective == "IDEAL_PARTNER"][:5]
    me_bits = [s.label.lower() for s in signals if s.perspective == "ME"][:3]
    narrative = (
        "I'm looking for someone who is " + ", ".join(ideal_bits) + ". "
        "As for me, I'd describe myself as " + ", ".join(me_bits) + "."
    )
    return Persona(id=persona_id, narrative=narrative, signals=signals)


def generate_profile_pool(n: int, seed: int | None = None) -> list[Persona]:
    rng = random.Random(seed)
    return [generate_random_profile(rng, f"baseline-{i}") for i in range(n)]


# --- Minimal local retrieval (no embedding API, no external deps) ---------
# A small bag-of-words / term-frequency cosine similarity is enough to
# demonstrate real retrieval mechanics (rank personas by relevance to a
# query) without requiring network access or an API key to run the tests.

def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _term_freq(tokens: list[str]) -> dict[str, float]:
    freq: dict[str, float] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0.0) + 1.0
    return freq


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    shared = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def persona_text(persona: Persona) -> str:
    """Everything about a persona that's searchable: the narrative plus
    every signal label, so retrieval can match on either."""
    return persona.narrative + " " + " ".join(s.label for s in persona.signals)


def build_index(personas: list[Persona]) -> list[tuple[Persona, dict[str, float]]]:
    return [(p, _term_freq(_tokenize(persona_text(p)))) for p in personas]


def retrieve_similar(
    query_text: str, index: list[tuple[Persona, dict[str, float]]], k: int = 5
) -> list[tuple[Persona, float]]:
    """Rank the pool by cosine similarity to `query_text`, highest first."""
    query_vec = _term_freq(_tokenize(query_text))
    scored = [(persona, _cosine_similarity(query_vec, vec)) for persona, vec in index]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    pool = generate_profile_pool(20, seed=42)
    index = build_index(pool)
    query = "I want someone who is warm, family-oriented, and loves quiet evenings at home."
    for persona, score in retrieve_similar(query, index, k=3):
        print(f"{score:.3f}  {persona.id}  {persona.narrative}")
