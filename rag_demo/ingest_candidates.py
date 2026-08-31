"""
rag_demo — seeds the real `candidates` table (Postgres/pgvector only) for
the RAG matching feature.

Generates N self-profile personas (generate_personas.generate_candidate_pool
— narrative + extracted `me` signals, run through anaphora_backend's real
extraction chain), assigns synthetic display metadata (name/age/gender —
presentation-layer data with no bearing on the psychometric trait sampling),
computes a real OpenAI embedding per candidate, and writes everything into
the live `candidates` table via the backend's own SQLAlchemy session — the
exact models the /matches endpoint reads from, not a side JSON file.

Requires:
  - OPENAI_API_KEY (candidate narratives + extraction + embeddings)
  - DATABASE_URL pointing at the real Postgres instance with
    `CREATE EXTENSION vector;` already run (see anaphora_backend/README.md)
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from generate_personas import generate_candidate_persona
from profiles import persona_text

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "anaphora_backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Synthetic display names only — not sourced from any real dataset or real
# person, same principle as STYLE_SEED_EXAMPLES in generate_personas.py.
# Deliberately plain/common first names across a few cultural backgrounds
# for a bit of variety without trying to be exhaustive.
FIRST_NAMES = {
    "female": [
        "Mia", "Sofia", "Amara", "Lena", "Priya", "Chloe", "Nadia", "Elena",
        "Yuki", "Zara", "Ines", "Camille", "Aisha", "Noor", "Freya",
    ],
    "male": [
        "Liam", "Diego", "Kai", "Omar", "Theo", "Jamal", "Lucas", "Arjun",
        "Felix", "Ravi", "Noah", "Idris", "Mateo", "Sami", "Anton",
    ],
    "nonbinary": [
        "River", "Sasha", "Jules", "Rowan", "Kit", "Noa", "Ari", "Quinn",
    ],
}

# Which of the 5 gender/photo buckets get a real photo (see
# frontend/public/candidates/README.md for the file naming convention) —
# only the first N candidates generated in each bucket get one, the rest
# fall back to an initials avatar in the UI. Order matters: these are
# assigned in generation order within each bucket.
PHOTO_FILES = {
    "male": ["/candidates/m1.jpg", "/candidates/m2.jpg", "/candidates/m3.jpg"],
    "female": ["/candidates/f1.jpg", "/candidates/f2.jpg"],
    "nonbinary": ["/candidates/a1.jpg", "/candidates/a2.jpg"],
}

# Roughly even male/female split with a smaller nonbinary share — arbitrary
# for a synthetic demo pool, not a claim about real population proportions.
GENDER_WEIGHTS = [("male", 0.45), ("female", 0.45), ("nonbinary", 0.10)]


def _assign_demographics(rng: random.Random, n: int) -> list[dict]:
    """Deterministic-given-seed assignment of gender/name/age/photo to n
    candidate slots, independent of trait sampling (these are display
    fields only, not psychometric data)."""
    genders = rng.choices(
        [g for g, _ in GENDER_WEIGHTS], weights=[w for _, w in GENDER_WEIGHTS], k=n
    )
    name_pools = {g: list(names) for g, names in FIRST_NAMES.items()}
    for pool in name_pools.values():
        rng.shuffle(pool)
    photo_pools = {g: list(files) for g, files in PHOTO_FILES.items()}

    demographics = []
    name_idx = {g: 0 for g in name_pools}
    for gender in genders:
        pool = name_pools[gender]
        name = pool[name_idx[gender] % len(pool)]
        name_idx[gender] += 1
        photo_url = photo_pools[gender].pop(0) if photo_pools[gender] else None
        demographics.append({
            "gender": gender,
            "name": name,
            "age": rng.randint(24, 42),
            "photo_url": photo_url,
        })
    return demographics


def ingest(n: int, seed: int | None = None, clear: bool = False) -> int:
    from app.database import SessionLocal, engine
    from app.models import Candidate
    from langchain_openai import OpenAIEmbeddings
    from app.config import settings

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
                persona = generate_candidate_persona(rng, f"candidate-{i}", use_llm=True)
                demo = demographics[i]
                signal_dicts = [s.as_dict() for s in persona.signals]
                embedding_text = persona_text(persona)
                embedding = embedder.embed_query(embedding_text)

                db.add(Candidate(
                    name=demo["name"],
                    age=demo["age"],
                    gender=demo["gender"],
                    photo_url=demo["photo_url"],
                    narrative=persona.narrative,
                    signals=signal_dicts,
                    embedding=embedding,
                ))
                # Committed per-candidate, not once at the end: each candidate
                # costs real narrative + extraction + embedding API calls, so a
                # late failure (DB hiccup, one bad API response) must not throw
                # away every candidate generated before it in the same run.
                db.commit()
                succeeded += 1
                print(f"  [{i + 1}/{n}] {demo['name']} ({demo['gender']}, {demo['age']}) — {len(signal_dicts)} signals")
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
    print(f"\nIngested {count} candidates into the candidates table.")


if __name__ == "__main__":
    _main()
