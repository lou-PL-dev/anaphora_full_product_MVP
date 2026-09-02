"""
rag_demo — seeds the real `candidates` table (Postgres/pgvector only) for
the reciprocal RAG matching feature.

Each synthetic candidate carries BOTH Blueprint perspectives:
- ME: who the candidate is
- IDEAL_PARTNER: who the candidate wants

It also carries deterministic demographic-preference metadata inside the
existing JSON `signals` field. This lets the live matcher evaluate age/gender
eligibility in both directions without adding demo-only database columns.

Broad retrieval embeddings are still built from ME only, so candidate desires
or demographic preferences do not contaminate the first-pass semantic search.

Requires:
  - OPENAI_API_KEY
  - DATABASE_URL pointing at Postgres with pgvector enabled
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from generate_reciprocal_candidates import (
    candidate_me_embedding_text,
    generate_reciprocal_candidate_persona,
)

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "anaphora_backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Sized with headroom above the default -n 50 pool (~45% male, ~45% female,
# ~10% nonbinary — see GENDER_WEIGHTS) so a normal run doesn't need to reuse
# a name at all; _assign_demographics still cycles the pool if it ever runs
# out rather than erroring.
FIRST_NAMES = {
    "female": [
        "Mia", "Sofia", "Amara", "Lena", "Priya", "Chloe", "Nadia", "Elena",
        "Yuki", "Zara", "Ines", "Camille", "Aisha", "Noor", "Freya",
        "Maya", "Isla", "Naomi", "Leila", "Talia", "Ana", "Hana", "Selin",
        "Mira", "Ida", "Wren", "Odette", "Marisol", "Thandiwe", "Keiko",
    ],
    "male": [
        "Liam", "Diego", "Kai", "Omar", "Theo", "Jamal", "Lucas", "Arjun",
        "Felix", "Ravi", "Noah", "Idris", "Mateo", "Sami", "Anton",
        "Ezra", "Amir", "Hugo", "Kenji", "Malik", "Tomas", "Gabriel", "Emir",
        "Rafael", "Bilal", "Soren", "Elias", "Nikolai", "Cyrus", "Tariq",
    ],
    "nonbinary": [
        "River", "Sasha", "Jules", "Rowan", "Kit", "Noa", "Ari", "Quinn",
        "Remy", "Skylar", "Indigo", "Tobin",
    ],
}

PHOTO_FILES = {
    "male": ["/candidates/m1.jpg", "/candidates/m2.jpg", "/candidates/m3.jpg", "/candidates/m4.jpg"],
    "female": ["/candidates/f1.jpg", "/candidates/f2.jpg", "/candidates/f3.jpg", "/candidates/f4.jpg"],
    "nonbinary": ["/candidates/a1.jpg", "/candidates/a2.jpg"],
}

GENDER_WEIGHTS = [("male", 0.45), ("female", 0.45), ("nonbinary", 0.10)]
DEMOGRAPHIC_PREFERENCE_GENDERS = ["male", "female", "nonbinary", "other"]


def _sample_demographic_preferences(rng: random.Random, age: int) -> dict:
    """Small synthetic eligibility profile, independent from Blueprint traits.

    The distribution is intentionally broad for the MVP candidate pool: it is
    there to exercise reciprocal eligibility, not to model population-level
    dating preferences.
    """
    if rng.random() < 0.15:
        gender_preferences = ["everyone"]
    else:
        count = 2 if rng.random() < 0.35 else 1
        gender_preferences = rng.sample(DEMOGRAPHIC_PREFERENCE_GENDERS, k=count)

    age_min = max(18, age - rng.randint(6, 14))
    age_max = min(70, age + rng.randint(8, 18))
    if age_max < age_min:
        age_max = age_min

    return {
        "kind": "demographic_preferences",
        "gender_preferences": gender_preferences,
        "age_min": age_min,
        "age_max": age_max,
    }


def _assign_demographics(rng: random.Random, n: int) -> list[dict]:
    genders = rng.choices(
        [g for g, _ in GENDER_WEIGHTS], weights=[w for _, w in GENDER_WEIGHTS], k=n
    )
    name_pools = {g: list(names) for g, names in FIRST_NAMES.items()}
    for pool in name_pools.values():
        rng.shuffle(pool)

    demographics = []
    name_idx = {g: 0 for g in name_pools}
    for gender in genders:
        pool = name_pools[gender]
        name = pool[name_idx[gender] % len(pool)]
        name_idx[gender] += 1
        # Only 2-4 photos exist per gender for this testing-only pool, so
        # candidates necessarily share photos — pick uniformly at random
        # rather than handing out each photo once and leaving the rest of
        # the pool with none at all.
        photo_url = rng.choice(PHOTO_FILES[gender]) if PHOTO_FILES.get(gender) else None
        age = rng.randint(24, 42)
        demographics.append({
            "gender": gender,
            "name": name,
            "age": age,
            "photo_url": photo_url,
            "demographic_preferences": _sample_demographic_preferences(rng, age),
        })
    return demographics


def ingest(n: int, seed: int | None = None, clear: bool = False) -> int:
    from app.config import settings
    from app.database import SessionLocal, engine
    from app.models import Candidate
    from langchain_openai import OpenAIEmbeddings

    if engine.dialect.name != "postgresql":
        raise RuntimeError(
            "candidates requires Postgres with pgvector — DATABASE_URL is currently "
            f"'{engine.dialect.name}'. Set DATABASE_URL to your Postgres instance first."
        )

    rng = random.Random(seed)
    demographics = _assign_demographics(rng, n)
    embedder = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)

    db = SessionLocal()
    succeeded = 0
    try:
        if clear:
            db.query(Candidate).delete()
            db.commit()

        for i in range(n):
            try:
                persona = generate_reciprocal_candidate_persona(
                    rng, f"candidate-{i}", use_llm=True
                )
                demo = demographics[i]
                signal_dicts = [s.as_dict() for s in persona.signals]
                signal_dicts.append(demo["demographic_preferences"])
                embedding = embedder.embed_query(candidate_me_embedding_text(persona))

                me_count = sum(1 for s in persona.signals if s.perspective == "ME")
                ideal_count = sum(1 for s in persona.signals if s.perspective == "IDEAL_PARTNER")
                us_count = sum(1 for s in persona.signals if s.perspective == "US")

                db.add(Candidate(
                    name=demo["name"],
                    age=demo["age"],
                    gender=demo["gender"],
                    photo_url=demo["photo_url"],
                    narrative=persona.narrative,
                    signals=signal_dicts,
                    embedding=embedding,
                ))
                db.commit()
                succeeded += 1
                prefs = demo["demographic_preferences"]
                print(
                    f"  [{i + 1}/{n}] {demo['name']} ({demo['gender']}, {demo['age']}) "
                    f"— ME {me_count} / IDEAL_PARTNER {ideal_count} / US {us_count} signals "
                    f"— open to {','.join(prefs['gender_preferences'])} {prefs['age_min']}–{prefs['age_max']}"
                )
            except Exception as e:
                db.rollback()
                print(f"  [{i + 1}/{n}] FAILED — {e!r} — continuing with the rest")
    finally:
        db.close()

    return succeeded


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", type=int, default=50, help="candidate pool size")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clear", action="store_true", help="delete existing candidates before ingesting")
    args = parser.parse_args()

    count = ingest(args.n, seed=args.seed, clear=args.clear)
    print(f"\nIngested {count} reciprocal candidates into the candidates table.")


if __name__ == "__main__":
    _main()
