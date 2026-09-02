"""Focused tests for Iteration 5 relationship-level reasoning."""
from unittest.mock import MagicMock, patch

from app.chains.relationship_reasoning_chain import assess_relationship_candidates
from app.models import BlueprintSignal, Candidate
from app.schemas import FitLevel, MatchExplanation, MatchExplanationsResult, MatchSection


def _candidate() -> Candidate:
    return Candidate(
        id="c1",
        name="Alex",
        age=34,
        gender="male",
        narrative="I am calm, affectionate and direct when something is wrong.",
        signals=[
            {"perspective": "ME", "category": "personality", "label": "Emotionally steady"},
            {"perspective": "ME", "category": "relationship_dynamic", "label": "Talks through conflict"},
            {"perspective": "IDEAL_PARTNER", "category": "personality", "label": "Warm and curious"},
            {"perspective": "IDEAL_PARTNER", "category": "relationship_dynamic", "label": "Comfortable with independence"},
        ],
    )


def test_relationship_reasoner_preserves_qualitative_fit():
    candidate = _candidate()
    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanation(
            candidate_id="c1",
            has_genuine_match=True,
            recommended_fit=FitLevel.strong_fit,
            sections=[MatchSection(heading="Why this could work", body="There is reciprocal evidence around steadiness and independence.")],
        )
    ])
    structured = MagicMock()
    structured.invoke.return_value = fake_result
    llm = MagicMock()
    llm.with_structured_output.return_value = structured

    with patch("app.llm.ChatOpenAI", return_value=llm):
        verdicts = assess_relationship_candidates(
            "USER IDEAL_PARTNER: emotionally steady\nUSER ME: warm and independent",
            [(candidate, ["USER WANTS -> CANDIDATE IS: steadiness", "CANDIDATE WANTS -> USER IS: independence"], True)],
        )

    has_match, fit, sections = verdicts["c1"]
    assert has_match is True
    assert fit == FitLevel.strong_fit
    assert sections


def test_relationship_reasoner_fails_closed_and_drops_sections():
    candidate = _candidate()
    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanation(
            candidate_id="c1",
            has_genuine_match=False,
            recommended_fit=FitLevel.strong_fit,
            sections=[MatchSection(heading="Should disappear", body="This must not be surfaced.")],
        )
    ])
    structured = MagicMock()
    structured.invoke.return_value = fake_result
    llm = MagicMock()
    llm.with_structured_output.return_value = structured

    with patch("app.llm.ChatOpenAI", return_value=llm):
        verdicts = assess_relationship_candidates("USER BLUEPRINT", [(candidate, [], True)])

    assert verdicts["c1"] == (False, None, [])


def test_relationship_reasoner_defaults_genuine_uncertain_fit_to_worth_exploring():
    candidate = _candidate()
    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanation(
            candidate_id="c1",
            has_genuine_match=True,
            recommended_fit=None,
            sections=[MatchSection(heading="Something to explore", body="The evidence is promising but still incomplete.")],
        )
    ])
    structured = MagicMock()
    structured.invoke.return_value = fake_result
    llm = MagicMock()
    llm.with_structured_output.return_value = structured

    with patch("app.llm.ChatOpenAI", return_value=llm):
        verdicts = assess_relationship_candidates("USER BLUEPRINT", [(candidate, [], True)])

    assert verdicts["c1"][1] == FitLevel.worth_exploring


if __name__ == "__main__":
    test_relationship_reasoner_preserves_qualitative_fit()
    test_relationship_reasoner_fails_closed_and_drops_sections()
    test_relationship_reasoner_defaults_genuine_uncertain_fit_to_worth_exploring()
    print("ALL RELATIONSHIP REASONING TESTS PASSED")
