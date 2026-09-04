"""Create one synthetic golden candidate for an existing demo user.

The fixture mirrors the user's current Blueprint in both directions:
  USER IDEAL_PARTNER -> CANDIDATE ME
  CANDIDATE IDEAL_PARTNER -> USER ME
  USER US <-> CANDIDATE US

It upserts one stable candidate and never clears the rest of the pool.

Usage:
  python seed_demo_match.py --user-id <uuid>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "anaphora_backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.chains.matching_chain import _normalise_gender, _normalise_gender_preferences
from app.llm import get_embedder
from app.models import BlueprintSignal, Candidate, User


DEMO_CANDIDATE_PREFIX = "anaphora-demo-match-"
DEFAULT_PHOTOS = {
    "male": "/candidates/m1.jpg",
    "female": "/candidates/f1.jpg",
    "nonbinary": "/candidates/a1.jpg",
}
GENDER_ORDER = ("male", "female", "nonbinary", "other")


def demo_candidate_id(user_id: str) -> str:
    return f"{DEMO_CANDIDATE_PREFIX}{user_id}"


def _preferred_age_bounds(value: str | None) -> tuple[int | None, int | None]:
    if not value:
        return None, None
    try:
        low, high = value.split("-", 1)
        return int(low), int(high)
    except (TypeError, ValueError):
        return None, None


def _candidate_gender(user: User, override: str | None) -> str:
    allowed = _normalise_gender_preferences(user.gender_preference)
    chosen = _normalise_gender(override) if override else None
    if chosen:
        if allowed and "everyone" not in allowed and chosen not in allowed:
            raise ValueError(
                f"Candidate gender '{chosen}' is outside this user's preference: {sorted(allowed)}"
            )
        return chosen
    if allowed and "everyone" not in allowed:
        for gender in GENDER_ORDER:
            if gender in allowed:
                return gender
        raise ValueError(f"No supported candidate gender in preference: {sorted(allowed)}")
    return "male"


def _candidate_age(user: User, override: int | None) -> int:
    low, high = _preferred_age_bounds(user.preferred_age_range)
    if override is not None:
        if ((low is not None and override < low)
                or (high is not None and override > high)):
            raise ValueError(f"Candidate age {override} is outside the preferred range {low}-{high}")
        return override
    if low is not None and high is not None:
        return (low + high) // 2
    return max(18, min(70, user.age or 35))


def _copy_signal(signal: BlueprintSignal, perspective: str) -> dict:
    return {
        "perspective": perspective,
        "category": signal.category,
        "label": signal.label,
        "strength": signal.strength or "preference",
        "evidence_text": signal.evidence_text or signal.label,
        "confidence": 1.0,
    }


def _natural_list(labels: list[str], limit: int = 3) -> str:
    selected = [label.strip() for label in labels if label and label.strip()][:limit]
    if not selected:
        return "what matters to you"
    if len(selected) == 1:
        return selected[0]
    return ", ".join(selected[:-1]) + f" and {selected[-1]}"


def build_demo_candidate_payload(
    user: User,
    signals: list[BlueprintSignal],
    *,
    name: str = "Alex",
    gender: str | None = None,
    age: int | None = None,
    photo_url: str | None = None,
) -> dict:
    user_me = [signal for signal in signals if signal.perspective == "ME"]
    user_ideal = [signal for signal in signals if signal.perspective == "IDEAL_PARTNER"]
    user_us = [signal for signal in signals if signal.perspective == "US"]
    if not user_ideal:
        raise ValueError("The demo user has no IDEAL_PARTNER signals")
    if not user_me:
        raise ValueError("The demo user has no ME signals")

    resolved_gender = _candidate_gender(user, gender)
    resolved_age = _candidate_age(user, age)
    forward_labels = [signal.label for signal in user_ideal]
    reverse_labels = [signal.label for signal in user_me]
    relationship_labels = [signal.label for signal in user_us]

    narrative = (
        f"I'm someone who values {_natural_list(forward_labels)}. "
        f"I'm drawn to a person who brings {_natural_list(reverse_labels)}."
    )
    if relationship_labels:
        narrative += f" In a relationship, {_natural_list(relationship_labels)} matter to me."

    fallback_sections = [{
        "heading": "Why this could work",
        "body": (
            f"{name} reflects several things you said matter: {_natural_list(forward_labels)}. "
            f"What {name} is looking for also aligns with how you described yourself: "
            f"{_natural_list(reverse_labels)}."
        ),
    }]
    if relationship_labels:
        fallback_sections.append({
            "heading": "How you might connect",
            "body": f"You both make room for {_natural_list(relationship_labels)} in a relationship.",
        })

    candidate_signals = [_copy_signal(signal, "ME") for signal in user_ideal]
    candidate_signals.extend(_copy_signal(signal, "IDEAL_PARTNER") for signal in user_me)
    candidate_signals.extend(_copy_signal(signal, "US") for signal in user_us)
    candidate_signals.extend([
        {
            "kind": "demographic_preferences",
            "gender_preferences": ["everyone"],
            "age_min": 18,
            "age_max": 99,
        },
        {
            "kind": "demo_fixture",
            "target_user_id": user.id,
            "fallback_sections": fallback_sections,
        },
    ])
    embedding_text = narrative + " " + " ".join(forward_labels)
    return {
        "id": demo_candidate_id(user.id),
        "name": name,
        "age": resolved_age,
        "gender": resolved_gender,
        "photo_url": photo_url or DEFAULT_PHOTOS.get(resolved_gender),
        "narrative": narrative,
        "signals": candidate_signals,
        "embedding_text": embedding_text,
    }


def seed_demo_match(
    user_id: str,
    *,
    name: str = "Alex",
    gender: str | None = None,
    age: int | None = None,
    photo_url: str | None = None,
) -> Candidate:
    from app.database import SessionLocal, engine

    if engine.dialect.name != "postgresql":
        raise RuntimeError("Demo matching requires DATABASE_URL to point at Postgres with pgvector")

    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            raise ValueError(f"No user found with id '{user_id}'")
        signals = db.query(BlueprintSignal).filter(BlueprintSignal.user_id == user_id).all()
        payload = build_demo_candidate_payload(
            user, signals, name=name, gender=gender, age=age, photo_url=photo_url,
        )
        embedding = get_embedder().embed_query(payload.pop("embedding_text"))
        candidate = db.get(Candidate, payload["id"])
        if candidate is None:
            candidate = Candidate(**payload, embedding=embedding)
        else:
            for key, value in payload.items():
                setattr(candidate, key, value)
            candidate.embedding = embedding
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", required=True, help="Tester UUID from the admin dashboard")
    parser.add_argument("--name", default="Alex")
    parser.add_argument("--gender", choices=GENDER_ORDER)
    parser.add_argument("--age", type=int)
    parser.add_argument("--photo-url")
    args = parser.parse_args()

    candidate = seed_demo_match(
        args.user_id,
        name=args.name,
        gender=args.gender,
        age=args.age,
        photo_url=args.photo_url,
    )
    print(
        f"Demo candidate ready: {candidate.name} ({candidate.gender}, {candidate.age}) "
        f"id={candidate.id}"
    )
    print("Set ANAPHORA_DEMO_MODE=true on the backend for the final-LLM safeguard.")


if __name__ == "__main__":
    _main()
