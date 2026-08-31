"""
Tests for the RAG matching feature (chains/matching_chain.py,
routers/matching_router.py). Retrieval itself (pgvector cosine similarity)
needs a real Postgres instance with the vector extension enabled — nothing
in this repo can exercise that against SQLite, so this file covers what
CAN be tested without one: the deterministic shared_signals logic, the
generation step's LLM call (mocked) including its fallback behavior, the
schema shapes, and the router's dialect guard (which fires correctly
against the default local SQLite DB, confirmed directly below rather than
mocked). See anaphora_backend/README.md for how to verify retrieval itself
against the real deployed Postgres instance.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.chains.matching_chain import generate_match_explanations, shared_signals
from app.models import BlueprintSignal, Candidate
from app.schemas import MatchExplanationItem, MatchExplanationsResult


def test_shared_signals_case_insensitive_overlap():
    user_signals = [
        BlueprintSignal(label="Warm"),
        BlueprintSignal(label="Loves hiking"),
        BlueprintSignal(label="Direct communicator"),
    ]
    candidate_signals = [
        {"label": "warm"},  # case-insensitive match
        {"label": "Enjoys cooking"},  # no match
        {"label": "Direct communicator"},  # exact match
    ]
    result = shared_signals(user_signals, candidate_signals)
    assert set(result) == {"Warm", "Direct communicator"}


def test_shared_signals_empty_when_no_overlap():
    assert shared_signals([BlueprintSignal(label="Warm")], [{"label": "Cold"}]) == []


def test_generate_match_explanations_empty_candidates_short_circuits():
    # No ChatOpenAI mock needed here — an empty candidate list must never
    # trigger an LLM call at all.
    assert generate_match_explanations("some narrative", []) == {}


def test_generate_match_explanations_fills_gap_for_uncovered_candidate():
    """The schema requires the model to explain every candidate it's given,
    but real LLM output is never guaranteed exhaustive — confirms the
    deterministic fallback actually kicks in for a candidate the mocked
    model's response omits."""
    c1 = Candidate(id="c1", name="Alex", age=30, gender="nonbinary")
    c2 = Candidate(id="c2", name="Sam", age=28, gender="male")

    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanationItem(candidate_id="c1", explanation="You both value deep conversation."),
        # c2 deliberately omitted, to exercise the fallback
    ])
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = fake_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    with patch("app.chains.matching_chain.ChatOpenAI", return_value=mock_llm):
        explanations = generate_match_explanations(
            "Looking for someone warm and adventurous.",
            [(c1, ["Warm"]), (c2, [])],
        )

    assert explanations["c1"] == "You both value deep conversation."
    assert "c2" in explanations  # fallback text, not missing
    assert explanations["c2"]  # non-empty


def test_matches_endpoint_503_on_sqlite_dev_db():
    """The candidates table (pgvector) is Postgres-only — see the
    create_all() guard in main.py — so /matches must refuse cleanly on the
    default local SQLite dev DB rather than crash with a raw SQL error."""
    from app.main import app

    client = TestClient(app)
    r = client.get("/matches", headers={"X-Anaphora-User-Id": "test-matching-user"})
    assert r.status_code == 503
    assert "postgres" in r.json()["detail"].lower()


if __name__ == "__main__":
    test_shared_signals_case_insensitive_overlap()
    test_shared_signals_empty_when_no_overlap()
    test_generate_match_explanations_empty_candidates_short_circuits()
    test_generate_match_explanations_fills_gap_for_uncovered_candidate()
    test_matches_endpoint_503_on_sqlite_dev_db()
    print("ALL MATCHING TESTS PASSED")
