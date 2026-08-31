"""
Operation C — RAG matching: retrieve candidates whose OWN profile is close
to what the user wants, then have an LLM decide — honestly — whether there's
something genuine to say about each, per PRD section 26 (Match Presentation):

  "Anaphora deliberately avoids presenting: 92% compatible. Instead:
  Strong fit / Worth exploring. The product explains why."

  "Why Anaphora thinks you should meet / The life you're building / How you
  connect / Something you might enjoy / Something to explore [an honest
  tension] ... The explanation should only reference information
  legitimately available for matchmaking and should avoid unnecessarily
  exposing sensitive friend commentary."

No match_pct is ever computed for display — retrieval similarity is used
ONLY to rank and shortlist candidates internally. A candidate the LLM can't
say anything genuine and specific about is dropped entirely, never shown
with a generic fallback (see MatchExplanation.has_genuine_match).

Candidates are synthetic (see rag_demo/generate_personas.py +
ingest_candidates.py), not real users — this is a demo-scope matching
layer, not the production recommender the PRD deliberately excludes.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.orm import Session

from ..config import settings
from ..models import BlueprintSignal, Candidate
from ..schemas import CandidateOut, FitLevel, MatchExplanationsResult, MatchOut, MatchSection

# How many candidates to shortlist by embedding similarity before the LLM
# judges genuineness, vs. how many "genuine" matches to actually show. Wider
# shortlist than display count on purpose — "depth over volume" (PRD
# Product Principles) means most of the shortlist is expected to get
# filtered out, not that the shortlist itself should be small.
RETRIEVAL_SHORTLIST_SIZE = 8
MAX_MATCHES_SHOWN = 5

MATCH_SYSTEM_PROMPT = """You decide, honestly, whether there's something genuine and specific to say \
about why the user and each candidate could be a good match — in Anaphora's voice: warm, intelligent, \
respectful, human. You speak like a thoughtful friend, not a sales pitch or a compatibility algorithm.

For EACH candidate:
- Set has_genuine_match to true ONLY if you can write 1-4 short, SPECIFIC sections grounded in what's \
actually given for that candidate (their shared_signals overlap with the user, and both people's \
narratives). A thin, generic, or purely coincidental overlap does NOT count as genuine.
- If there's nothing specific and real to point to, set has_genuine_match to FALSE and leave sections \
empty. This is not a failure — saying nothing honest beats saying something vague and confident-sounding. \
Do not pad a weak match with invented specifics to make it sound stronger than it is.
- When has_genuine_match is true, write sections in Anaphora's own style — natural headings like "The \
life you're building", "How you connect", "Something you might enjoy". You may ALSO honestly name a real \
tension under a heading like "Something to explore" (e.g. one is more spontaneous with money, the other \
more of a planner) if the narratives genuinely support one — this builds trust, it isn't a downside to hide.
- Every sentence must be traceable to the shared_signals or narrative text actually given. Never invent \
a shared interest, value, or trait. Never reference anything about a candidate beyond what's given here — \
in particular, never invent or expose any friend-contributed commentary, since that's never legitimately \
available for this kind of explanation."""


def _signal_labels(signals: list[dict]) -> set[str]:
    return {s["label"].strip().lower() for s in signals if s.get("label")}


def _embedding_text(narrative: str, signal_labels: list[str]) -> str:
    return (narrative or "") + " " + " ".join(signal_labels)


def embed_text(text: str) -> list[float]:
    embedder = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    return embedder.embed_query(text)


def retrieve_candidates(db: Session, query_embedding: list[float], k: int = RETRIEVAL_SHORTLIST_SIZE) -> list[tuple[Candidate, float]]:
    """Returns (candidate, similarity 0-1) pairs, closest first — similarity
    is used ONLY to rank/shortlist internally, never shown to the user (see
    module docstring). Postgres/pgvector only — Candidate.embedding.cosine_distance
    is a pgvector SQLAlchemy comparator with no SQLite equivalent (see the
    create_all() guard in main.py for why that table doesn't exist there)."""
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
    ideal_partner signals. Feeds the LLM's grounding — not displayed
    directly to the user anymore (PRD section 26 wants prose, not a raw
    signal-overlap list)."""
    user_labels = {s.label.strip().lower(): s.label for s in user_ideal_partner_signals}
    candidate_labels = _signal_labels(candidate_signals)
    return [user_labels[label] for label in candidate_labels if label in user_labels]


def judge_and_explain_candidates(
    user_narrative: str, candidates: list[tuple[Candidate, list[str]]]
) -> dict[str, tuple[bool, list[MatchSection]]]:
    """One LLM call judges AND explains every shortlisted candidate at once.
    Returns {candidate_id: (has_genuine_match, sections)}. Any candidate_id
    the model's output doesn't cover at all is treated as no genuine match
    (fail closed — never show a candidate the model didn't explicitly vouch
    for)."""
    if not candidates:
        return {}

    candidates_block = "\n\n".join(
        f"candidate_id: {c.id}\n"
        f"candidate's own narrative: {c.narrative}\n"
        f"shared_signals with the user: {shared or '(none)'}"
        for c, shared in candidates
    )
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.3, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(MatchExplanationsResult)
    result = structured_llm.invoke([
        {"role": "system", "content": MATCH_SYSTEM_PROMPT},
        {"role": "user", "content": f"What the user is looking for:\n{user_narrative}\n\nCandidates:\n{candidates_block}"},
    ])
    return {
        item.candidate_id: (item.has_genuine_match, item.sections if item.has_genuine_match else [])
        for item in result.explanations
    }


def find_matches(db: Session, user_narrative: str, user_ideal_partner_signals: list[BlueprintSignal]) -> list[MatchOut]:
    query_text = _embedding_text(user_narrative or "", [s.label for s in user_ideal_partner_signals])
    query_embedding = embed_text(query_text)
    retrieved = retrieve_candidates(db, query_embedding, k=RETRIEVAL_SHORTLIST_SIZE)

    candidates_with_shared = [
        (candidate, shared_signals(user_ideal_partner_signals, candidate.signals or []))
        for candidate, _similarity in retrieved
    ]
    judged = judge_and_explain_candidates(user_narrative or "", candidates_with_shared)

    # retrieved is already similarity-sorted (closest first) — filtering
    # preserves that order, so the first survivor is the closest genuine
    # match and gets "strong_fit"; the rest that passed get "worth_exploring".
    genuine = [
        (candidate, sections)
        for candidate, _similarity in retrieved
        for has_genuine, sections in [judged.get(candidate.id, (False, []))]
        if has_genuine and sections
    ][:MAX_MATCHES_SHOWN]

    return [
        MatchOut(
            candidate=CandidateOut.model_validate(candidate),
            fit=FitLevel.strong_fit if i == 0 else FitLevel.worth_exploring,
            sections=sections,
        )
        for i, (candidate, sections) in enumerate(genuine)
    ]
