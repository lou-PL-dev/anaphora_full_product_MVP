from unittest.mock import MagicMock, patch

import pytest

from seed_demo_match import build_demo_candidate_payload, demo_candidate_id
from app.chains.matching_chain import semantic_rerank_candidates
from app.chains.matching_chain_v5 import deterministic_fit_ceiling
from app.models import BlueprintSignal, Candidate, User
from app.schemas import FitLevel


def _signal(perspective: str, category: str, label: str) -> BlueprintSignal:
    return BlueprintSignal(
        user_id="u1",
        perspective=perspective,
        category=category,
        label=label,
        strength="strong_preference",
        evidence_text=label,
        confidence=1.0,
    )


def _demo_user_and_signals():
    user = User(
        id="u1",
        gender="woman",
        gender_preference="men",
        age=37,
        preferred_age_range="35-45",
    )
    signals = [
        _signal("IDEAL_PARTNER", "personality", "Warm and emotionally available"),
        _signal("IDEAL_PARTNER", "lifestyle", "Active and adventurous"),
        _signal("IDEAL_PARTNER", "physical_type", "Dark hair and a solid build"),
        _signal("ME", "personality", "Playful and ambitious"),
        _signal("ME", "lifestyle", "Balances friends with quiet evenings"),
        _signal("ME", "core_values", "Honest and direct"),
        _signal("US", "relationship_shape", "An equal partnership"),
    ]
    return user, signals


def test_demo_candidate_mirrors_the_user_in_both_directions():
    user, signals = _demo_user_and_signals()
    payload = build_demo_candidate_payload(user, signals, name="Alex")

    assert payload["id"] == demo_candidate_id("u1")
    assert payload["gender"] == "male"
    assert payload["age"] == 40
    assert payload["photo_url"] == "/candidates/m1.jpg"

    candidate_signals = payload["signals"]
    me_labels = {s["label"] for s in candidate_signals if s.get("perspective") == "ME"}
    ideal_labels = {
        s["label"] for s in candidate_signals if s.get("perspective") == "IDEAL_PARTNER"
    }
    assert "Warm and emotionally available" in me_labels
    assert "Playful and ambitious" in ideal_labels
    assert any(
        s.get("kind") == "demo_fixture" and s.get("target_user_id") == "u1"
        for s in candidate_signals
    )


def test_demo_candidate_rejects_an_ineligible_manual_override():
    user, signals = _demo_user_and_signals()
    with pytest.raises(ValueError, match="outside this user's preference"):
        build_demo_candidate_payload(user, signals, gender="female")


def test_demo_candidate_passes_reciprocal_deterministic_gate():
    user, signals = _demo_user_and_signals()
    payload = build_demo_candidate_payload(user, signals, name="Alex")
    candidate = Candidate(
        id=payload["id"],
        name=payload["name"],
        age=payload["age"],
        gender=payload["gender"],
        narrative=payload["narrative"],
        signals=payload["signals"],
    )
    user_ideal = [s for s in signals if s.perspective == "IDEAL_PARTNER"]
    user_me = [s for s in signals if s.perspective == "ME"]
    user_us = [s for s in signals if s.perspective == "US"]

    embedder = MagicMock()
    embedder.embed_documents.side_effect = lambda texts: [[1.0, 0.0] for _ in texts]
    with patch("app.llm.OpenAIEmbeddings", return_value=embedder):
        finalist = semantic_rerank_candidates(
            [(candidate, 1.0)],
            user_ideal,
            user_me_signals=user_me,
            user_us_signals=user_us,
            finalist_size=1,
        )[0]

    _candidate, score, forward, reverse, evidence, reciprocal_complete = finalist
    assert reciprocal_complete is True
    assert deterministic_fit_ceiling(
        score, forward, reverse, evidence, reciprocal_complete
    ) == FitLevel.strong_fit
