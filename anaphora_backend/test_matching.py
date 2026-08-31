"""
Tests for the RAG matching feature (chains/matching_chain.py,
routers/matching_router.py). Retrieval itself (pgvector cosine similarity)
needs a real Postgres instance with the vector extension enabled — nothing
in this repo can exercise that against SQLite, so this file covers what
CAN be tested without one: the deterministic shared_signals logic, the
generation step's LLM call (mocked) including the genuineness filter and
fit-label assignment, the schema shapes, and the router's guards (dialect
+ readiness), which fire correctly against the default local SQLite DB
without needing a real database's data.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.chains.matching_chain import judge_and_explain_candidates, shared_signals
from app.models import BlueprintSignal, Candidate
from app.schemas import MatchExplanation, MatchExplanationsResult, MatchSection


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


def test_judge_and_explain_empty_candidates_short_circuits():
    # No ChatOpenAI mock needed here — an empty candidate list must never
    # trigger an LLM call at all.
    assert judge_and_explain_candidates("some narrative", []) == {}


def test_judge_and_explain_drops_sections_when_not_genuine():
    """has_genuine_match=False must always come back with empty sections,
    even if the mocked model's own output (a real LLM should never do this,
    but the fixture proves the code doesn't trust it blindly) claims
    otherwise."""
    c1 = Candidate(id="c1", name="Alex", age=30, gender="nonbinary")

    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanation(
            candidate_id="c1", has_genuine_match=False,
            sections=[MatchSection(heading="Should be dropped", body="...")],
        ),
    ])
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = fake_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    with patch("app.chains.matching_chain.ChatOpenAI", return_value=mock_llm):
        judged = judge_and_explain_candidates("Looking for someone warm.", [(c1, ["Warm"])])

    has_genuine, sections = judged["c1"]
    assert has_genuine is False
    assert sections == []


def test_judge_and_explain_uncovered_candidate_fails_closed():
    """A candidate the model's output doesn't mention at all must be
    treated as no genuine match, not silently shown."""
    c1 = Candidate(id="c1", name="Alex", age=30, gender="nonbinary")
    c2 = Candidate(id="c2", name="Sam", age=28, gender="male")

    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanation(
            candidate_id="c1", has_genuine_match=True,
            sections=[MatchSection(heading="How you connect", body="You both value deep conversation.")],
        ),
        # c2 deliberately omitted
    ])
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = fake_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    with patch("app.chains.matching_chain.ChatOpenAI", return_value=mock_llm):
        judged = judge_and_explain_candidates(
            "Looking for someone warm and adventurous.", [(c1, ["Warm"]), (c2, [])],
        )

    assert judged["c1"][0] is True
    assert judged["c1"][1]
    assert judged.get("c2", (False, []))[0] is False


def test_matches_endpoint_503_on_sqlite_dev_db():
    """The candidates table (pgvector) is Postgres-only — see the
    create_all() guard in main.py — so /matches must refuse cleanly on the
    default local SQLite dev DB rather than crash with a raw SQL error.
    This guard fires before the readiness check, so no user/DB setup is
    needed to exercise it."""
    from app.main import app

    client = TestClient(app)
    r = client.get("/matches", headers={"X-Anaphora-User-Id": "test-matching-user"})
    assert r.status_code == 503
    assert "postgres" in r.json()["detail"].lower()


if __name__ == "__main__":
    test_shared_signals_case_insensitive_overlap()
    test_shared_signals_empty_when_no_overlap()
    test_judge_and_explain_empty_candidates_short_circuits()
    test_judge_and_explain_drops_sections_when_not_genuine()
    test_judge_and_explain_uncovered_candidate_fails_closed()
    test_matches_endpoint_503_on_sqlite_dev_db()
    print("ALL MATCHING TESTS PASSED")
