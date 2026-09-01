"""
rag_demo — seeds the real `candidates` table (Postgres/pgvector only) for
the reciprocal RAG matching feature.

Each synthetic candidate now carries BOTH Blueprint perspectives:
- ME: who the candidate is
- IDEAL_PARTNER: who the candidate wants

Broad retrieval embeddings are still built from ME only, so candidate desires
do not contaminate the first-pass search. The IDEAL_PARTNER side is consumed
later by reciprocal reranking.

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

PHOTO_FILES = {
    "male": ["/candidates/m1.jpg", "/candidates/m2.jpg", "/candidates/m3.jpg", "/candidates/m4.jpg"],
    "female": ["/candidates/f1.jpg", "/candidates/f2.jpg", "/candidates/f3.jpg", "/candidates/f4.jpg"],
    "nonbinary": ["/candidates/a1.jpg", "/candidates/a2.jpg"],
}

GENDER_WEIGHTS = [("male", 0.45), ("female", 0.45), ("nonbinary", 0.10)]


def _assign_demographics(rng: random.Random, n: int) -> list[dict]:
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
                embedding = embedder.embed_query(candidate_me_embedding_text(persona))

                me_count = sum(1 for s in persona.signals if s.perspective == "ME")
                ideal_count = sum(1 for s in persona.signals if s.perspective == "IDEAL_PARTNER")

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
                print(
                    f"  [{i + 1}/{n}] {demo['name']} ({demo['gender']}, {demo['age']}) "
                    f"— ME {me_count} / IDEAL_PARTNER {ideal_count} signals"
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
