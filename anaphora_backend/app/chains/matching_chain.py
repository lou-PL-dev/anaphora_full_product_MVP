"""
Operation C (new) — RAG matching: retrieve candidates whose OWN profile is
close to what the user wants, then generate a grounded explanation for each.

Retrieval = pgvector cosine similarity between the user's ideal_partner
Blueprint and each candidate's self-profile embedding (both embedded with
the same model — see config.embedding_model).
Generation = one structured-output LLM call that explains the retrieved
candidates, grounded ONLY in their deterministic shared_signals overlap —
never free-associating compatibility the data doesn't support.

Candidates are synthetic (see rag_demo/generate_personas.py +
ingest_candidates.py), not real users — this is a demo-scope matching
layer, not the production recommender the PRD deliberately excludes.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.orm import Session

from ..config import settings
from ..models import BlueprintSignal, Candidate
from ..schemas import CandidateOut, MatchExplanationsResult, MatchOut

MATCH_SYSTEM_PROMPT = """You write short, warm compatibility blurbs for a matchmaking app. \
For EACH candidate given, write one or two natural sentences on why they could be a good match \
for the user — grounded ONLY in that candidate's shared_signals list. Never invent a shared \
interest, value, or trait that isn't in shared_signals. If shared_signals is short or generic, \
write a shorter, more modest blurb rather than padding it with invented specifics."""


def _signal_labels(signals: list[dict]) -> set[str]:
    return {s["label"].strip().lower() for s in signals if s.get("label")}


def _embedding_text(narrative: str, signal_labels: list[str]) -> str:
    return (narrative or "") + " " + " ".join(signal_labels)


def embed_text(text: str) -> list[float]:
    embedder = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    return embedder.embed_query(text)


def retrieve_candidates(db: Session, query_embedding: list[float], k: int = 5) -> list[tuple[Candidate, float]]:
    """Returns (candidate, similarity 0-1) pairs, closest first. Postgres/
    pgvector only — Candidate.embedding.cosine_distance is a pgvector
    SQLAlchemy comparator with no SQLite equivalent (see the create_all()
    guard in main.py for why that table doesn't exist there at all)."""
    rows = (
        db.query(Candidate, Candidate.embedding.cosine_distance(query_embedding).label("distance"))
        .order_by("distance")
        .limit(k)
        .all()
    )
    # OpenAI's embeddings are unit-normalized, so cosine_distance is in
    # [0, 2]; similarity = 1 - distance is the standard conversion.
    return [(candidate, max(0.0, min(1.0, 1.0 - distance))) for candidate, distance in rows]


def shared_signals(user_ideal_partner_signals: list[BlueprintSignal], candidate_signals: list[dict]) -> list[str]:
    """Deterministic, non-hallucinated overlap: candidate signal labels that
    also appear (case-insensitive exact match) among the user's
    ideal_partner signals. Intentionally simple — this is the grounding
    fed to the LLM, not the match score itself (see retrieve_candidates)."""
    user_labels = {s.label.strip().lower(): s.label for s in user_ideal_partner_signals}
    candidate_labels = _signal_labels(candidate_signals)
    return [user_labels[label] for label in candidate_labels if label in user_labels]


def generate_match_explanations(
    user_narrative: str, candidates: list[tuple[Candidate, list[str]]]
) -> dict[str, str]:
    """One LLM call explains all retrieved candidates at once — same
    cost-conscious pattern as conversation_chain.converse(). Returns
    {candidate_id: explanation}; falls back to a deterministic blurb for
    any candidate the model's output doesn't cover (schema requires an
    explanation per given candidate_id, but real LLM output is never
    guaranteed to be perfectly exhaustive)."""
    if not candidates:
        return {}

    candidates_block = "\n\n".join(
        f"candidate_id: {c.id}\nshared_signals: {shared or '(none)'}"
        for c, shared in candidates
    )
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.3, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(MatchExplanationsResult)
    result = structured_llm.invoke([
        {"role": "system", "content": MATCH_SYSTEM_PROMPT},
        {"role": "user", "content": f"What the user is looking for:\n{user_narrative}\n\nCandidates:\n{candidates_block}"},
    ])
    explanations = {item.candidate_id: item.explanation for item in result.explanations}
    for c, shared in candidates:
        explanations.setdefault(
            c.id,
            f"You might click over {shared[0].lower()}." if shared else "Worth a conversation to see if it clicks.",
        )
    return explanations


def find_matches(db: Session, user_narrative: str, user_ideal_partner_signals: list[BlueprintSignal], k: int = 5) -> list[MatchOut]:
    query_embedding = embed_text(user_narrative or "")
    retrieved = retrieve_candidates(db, query_embedding, k=k)

    candidates_with_shared = [
        (candidate, shared_signals(user_ideal_partner_signals, candidate.signals or []))
        for candidate, _similarity in retrieved
    ]
    explanations = generate_match_explanations(user_narrative or "", candidates_with_shared)

    return [
        MatchOut(
            candidate=CandidateOut.model_validate(candidate),
            match_pct=round(similarity * 100),
            shared_signals=shared,
            explanation=explanations.get(candidate.id, ""),
        )
        for (candidate, similarity), (_candidate, shared) in zip(retrieved, candidates_with_shared)
    ]
