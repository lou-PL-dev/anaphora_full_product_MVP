"""Focused Iteration 4 tests that do not require Postgres or OpenAI calls."""

from app.chains.matching_chain import _candidate_signals, _reciprocal_score
from app.chains.matching_chain_v5 import (
    deterministic_fit_ceiling,
    _candidate_available_for_user,
    _demo_fallback_verdict,
)
from app.config import settings
from app.models import Candidate
from app.schemas import FitLevel


def test_reciprocal_score_penalizes_one_sided_fit():
    balanced = _reciprocal_score(0.78, 0.76, 0.70)
    one_sided = _reciprocal_score(0.95, 0.32, 0.70)
    assert balanced > one_sided


def test_reciprocal_score_not_naive_average():
    # These have similar arithmetic averages, but the pair with the weak
    # reverse direction should rank lower because the weaker side matters.
    balanced = _reciprocal_score(0.70, 0.70, 0.65)
    asymmetric = _reciprocal_score(0.95, 0.45, 0.65)
    assert balanced > asymmetric


def test_legacy_candidate_without_ideal_profile_is_not_strong_reciprocal_fit():
    complete = _reciprocal_score(0.78, 0.72, 0.70)
    legacy = _reciprocal_score(0.78, None, 0.70)
    assert complete > legacy


def test_candidate_signal_perspectives_are_kept_separate():
    candidate = Candidate(
        id="c1",
        name="Alex",
        age=34,
        gender="male",
        signals=[
            {"perspective": "ME", "category": "personality", "label": "Warm"},
            {"perspective": "IDEAL_PARTNER", "category": "personality", "label": "Playful"},
        ],
    )
    assert [s["label"] for s in _candidate_signals(candidate, "ME")] == ["Warm"]
    assert [s["label"] for s in _candidate_signals(candidate, "IDEAL_PARTNER")] == ["Playful"]


def test_old_candidate_signals_default_to_me_for_backwards_compatibility():
    candidate = Candidate(
        id="legacy",
        name="Sam",
        age=35,
        gender="female",
        signals=[{"category": "values", "label": "Community matters"}],
    )
    assert [s["label"] for s in _candidate_signals(candidate, "ME")] == ["Community matters"]
    assert _candidate_signals(candidate, "IDEAL_PARTNER") == []


def _evidence() -> list[str]:
    return [
        "USER WANTS -> CANDIDATE IS: personality: wants 'warm' (strong_preference); evidence 'warm'",
        "USER WANTS -> CANDIDATE IS: lifestyle: wants 'active' (preference); evidence 'cycles'",
        "CANDIDATE WANTS -> USER IS: personality: wants 'curious' (preference); evidence 'curious'",
        "CANDIDATE WANTS -> USER IS: core_values: wants 'honest' (strong_preference); evidence 'honest'",
        "SHARED RELATIONSHIP VISION: relationship_shape: wants 'equal' (preference); evidence 'equal'",
    ]


def test_fit_ceiling_rejects_top_ranked_but_weak_candidate():
    assert deterministic_fit_ceiling(0.49, 0.70, 0.70, _evidence(), True) is None


def test_fit_ceiling_requires_evidence_in_both_person_directions():
    one_sided = [item for item in _evidence() if not item.startswith("CANDIDATE WANTS")]
    assert deterministic_fit_ceiling(0.70, 0.70, 0.70, one_sided, True) is None


def test_fit_ceiling_distinguishes_worth_exploring_from_strong():
    assert deterministic_fit_ceiling(0.58, 0.50, 0.49, _evidence(), True) == FitLevel.worth_exploring
    assert deterministic_fit_ceiling(0.70, 0.65, 0.64, _evidence(), True) == FitLevel.strong_fit


def test_demo_fallback_is_opt_in_targeted_and_still_requires_fit_ceiling(monkeypatch):
    candidate = Candidate(
        id="anaphora-demo-match-u1",
        name="Alex",
        age=39,
        gender="male",
        signals=[{
            "kind": "demo_fixture",
            "target_user_id": "u1",
            "fallback_sections": [{
                "heading": "Why this could work",
                "body": "Alex reflects several preferences in this demo Blueprint.",
            }],
        }],
    )

    monkeypatch.setattr(settings, "anaphora_demo_mode", False)
    assert _candidate_available_for_user(candidate, "u1") is False
    assert _demo_fallback_verdict(candidate, "u1", FitLevel.strong_fit) is None

    monkeypatch.setattr(settings, "anaphora_demo_mode", True)
    assert _candidate_available_for_user(candidate, "someone-else") is False
    assert _candidate_available_for_user(candidate, "u1") is True
    assert _demo_fallback_verdict(candidate, "someone-else", FitLevel.strong_fit) is None
    assert _demo_fallback_verdict(candidate, "u1", None) is None

    has_match, fit, sections = _demo_fallback_verdict(
        candidate, "u1", FitLevel.strong_fit
    )
    assert has_match is True
    assert fit == FitLevel.strong_fit
    assert sections[0].heading == "Why this could work"
