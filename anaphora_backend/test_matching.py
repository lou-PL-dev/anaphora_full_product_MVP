"""
Tests for the RAG matching feature (chains/matching_chain.py,
routers/matching_router.py).

pgvector retrieval itself still needs Postgres. These tests cover the
deterministic overlap fallback, semantic reranking with mocked embeddings,
grounded LLM judgment, and router guards.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.chains.matching_chain import (
    FINALIST_SIZE,
    judge_and_explain_candidates,
    semantic_rerank_candidates,
    shared_signals,
)
from app.models import BlueprintSignal, Candidate
from app.schemas import MatchExplanation, MatchExplanationsResult, MatchSection


def test_shared_signals_case_insensitive_overlap():
    user_signals = [
        BlueprintSignal(label="Warm"),
        BlueprintSignal(label="Loves hiking"),
        BlueprintSignal(label="Direct communicator"),
    ]
    candidate_signals = [
        {"label": "warm"},
        {"label": "Enjoys cooking"},
        {"label": "Direct communicator"},
    ]
    result = shared_signals(user_signals, candidate_signals)
    assert set(result) == {"Warm", "Direct communicator"}


def test_shared_signals_empty_when_no_overlap():
    assert shared_signals([BlueprintSignal(label="Warm")], [{"label": "Cold"}]) == []


def test_shared_signals_catches_paraphrased_overlap():
    user_signals = [BlueprintSignal(label="Loves cooking at home")]
    candidate_signals = [{"label": "Enjoys cooking at home together"}]
    assert shared_signals(user_signals, candidate_signals) == ["Loves cooking at home"]


def test_shared_signals_does_not_match_opposite_polarity_on_shared_word():
    user_signals = [BlueprintSignal(label="Loves commitment")]
    candidate_signals = [{"label": "Avoids commitment"}]
    assert shared_signals(user_signals, candidate_signals) == []


def test_shared_signals_requires_more_than_one_shared_word():
    user_signals = [BlueprintSignal(label="Early riser")]
    candidate_signals = [{"label": "Late riser"}]
    assert shared_signals(user_signals, candidate_signals) == []


def test_shared_signals_dedupes_and_preserves_user_order():
    user_signals = [BlueprintSignal(label="Warm"), BlueprintSignal(label="Direct communicator")]
    candidate_signals = [{"label": "warm"}, {"label": "Warm"}, {"label": "Direct communicator"}]
    assert shared_signals(user_signals, candidate_signals) == ["Warm", "Direct communicator"]


def test_semantic_reranker_prefers_multi_category_evidence():
    user_signals = [
        BlueprintSignal(category="personality", label="Emotionally steady", strength="strong_preference", confidence=1.0),
        BlueprintSignal(category="lifestyle", label="Happy spending quiet evenings at home", strength="strong_preference", confidence=1.0),
        BlueprintSignal(category="relationship_dynamic", label="Talks through conflict calmly", strength="hard_requirement", confidence=1.0),
    ]
    broad_only = Candidate(
        id="broad", name="Broad", age=32, gender="male", signals=[
            {"category": "personality", "label": "Energetic and spontaneous"},
            {"category": "lifestyle", "label": "Out most nights"},
            {"category": "relationship_dynamic", "label": "Avoids difficult conversations"},
        ],
    )
    grounded = Candidate(
        id="grounded", name="Grounded", age=33, gender="male", signals=[
            {"category": "personality", "label": "Even-keeled and calm"},
            {"category": "lifestyle", "label": "Loves quiet nights at home"},
            {"category": "relationship_dynamic", "label": "Works through conflict by talking"},
        ],
    )

    # One-hot-ish fake semantic space. Candidate 2 is close to each user's
    # signal/category representation even though candidate 1 starts with a
    # higher broad retrieval score.
    def fake_embed_documents(texts):
        vectors = []
        for text in texts:
            low = text.lower()
            if any(term in low for term in ["steady", "even-keeled", "calm"]):
                vectors.append([1.0, 0.0, 0.0])
            elif any(term in low for term in ["quiet evenings", "quiet nights", "home"]):
                vectors.append([0.0, 1.0, 0.0])
            elif any(term in low for term in ["talks through conflict", "works through conflict", "talking"]):
                vectors.append([0.0, 0.0, 1.0])
            else:
                vectors.append([-1.0, -1.0, -1.0])
        return vectors

    mock_embedder = MagicMock()
    mock_embedder.embed_documents.side_effect = fake_embed_documents
    with patch("app.chains.matching_chain.OpenAIEmbeddings", return_value=mock_embedder):
        reranked = semantic_rerank_candidates(
            [(broad_only, 0.95), (grounded, 0.70)], user_signals, finalist_size=2
        )

    assert reranked[0][0].id == "grounded"
    assert len(reranked[0][2]) >= 2


def test_semantic_reranker_caps_finalists():
    user_signals = [BlueprintSignal(category="personality", label="Warm", strength="preference", confidence=1.0)]
    candidates = [
        (Candidate(id=f"c{i}", name=f"C{i}", age=30, gender="male", signals=[{"category": "personality", "label": "Warm"}]), 0.8)
        for i in range(FINALIST_SIZE + 3)
    ]
    mock_embedder = MagicMock()
    mock_embedder.embed_documents.side_effect = lambda texts: [[1.0, 0.0] for _ in texts]
    with patch("app.chains.matching_chain.OpenAIEmbeddings", return_value=mock_embedder):
        result = semantic_rerank_candidates(candidates, user_signals)
    assert len(result) == FINALIST_SIZE


def test_judge_and_explain_empty_candidates_short_circuits():
    assert judge_and_explain_candidates("structured preferences", []) == {}


def test_judge_and_explain_drops_sections_when_not_genuine():
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
        judged = judge_and_explain_candidates("personality: warm", [(c1, ["personality: warm ↔ warm"])])

    has_genuine, sections = judged["c1"]
    assert has_genuine is False
    assert sections == []


def test_judge_and_explain_uncovered_candidate_fails_closed():
    c1 = Candidate(id="c1", name="Alex", age=30, gender="nonbinary")
    c2 = Candidate(id="c2", name="Sam", age=28, gender="male")
    fake_result = MatchExplanationsResult(explanations=[
        MatchExplanation(
            candidate_id="c1", has_genuine_match=True,
            sections=[MatchSection(heading="How you connect", body="You both value deep conversation.")],
        ),
    ])
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = fake_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    with patch("app.chains.matching_chain.ChatOpenAI", return_value=mock_llm):
        judged = judge_and_explain_candidates(
            "personality: warm", [(c1, ["personality evidence"]), (c2, [])],
        )

    assert judged["c1"][0] is True
    assert judged["c1"][1]
    assert judged.get("c2", (False, []))[0] is False


def test_matches_endpoint_503_on_sqlite_dev_db():
    from app.main import app

    client = TestClient(app)
    r = client.get("/matches", headers={"X-Anaphora-User-Id": "test-matching-user"})
    assert r.status_code == 503
    assert "postgres" in r.json()["detail"].lower()


if __name__ == "__main__":
    test_shared_signals_case_insensitive_overlap()
    test_shared_signals_empty_when_no_overlap()
    test_semantic_reranker_prefers_multi_category_evidence()
    test_semantic_reranker_caps_finalists()
    test_judge_and_explain_empty_candidates_short_circuits()
    test_judge_and_explain_drops_sections_when_not_genuine()
    test_judge_and_explain_uncovered_candidate_fails_closed()
    test_matches_endpoint_503_on_sqlite_dev_db()
    print("ALL MATCHING TESTS PASSED")
