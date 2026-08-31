"""
Operation C — RAG matching: retrieve candidates whose OWN profile is close
to what the user wants, then have an LLM decide — honestly — whether there's
something genuine to say about each, per PRD section 26 (Match Presentation).

Explicit basic preferences such as gender and age are eligibility filters,
not soft semantic signals. They are applied before vector retrieval so an
otherwise-similar candidate outside those preferences never enters the
shortlist.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.orm import Session

from ..config import settings
from ..models import BlueprintSignal, Candidate
from ..schemas import CandidateOut, FitLevel, MatchExplanationsResult, MatchOut, MatchSection

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
empty. This is not a failure — saying nothing honest beats saying something vague and confident-sounding.
- When has_genuine_match is true, write sections in Anaphora's own style — natural headings like "The \
life you're building", "How you connect", "Something you might enjoy". You may ALSO honestly name a real \
tension under a heading like "Something to explore" if the narratives genuinely support one.
- Every sentence must be traceable to the shared_signals or narrative text actually given. Never invent \
a shared interest, value, or trait. Never expose friend-contributed commentary."""


def _signal_labels(signals: list[dict]) -> set[str]:
    return {s["label"].strip().lower() for s in signals if s.get("label")}


def _embedding_text(narrative: str, signal_labels: list[str]) -> str:
    return (narrative or "") + " " + " ".join(signal_labels)


def embed_text(text: str) -> list[float]:
    embedder = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    return embedder.embed_query(text)


def _normalise_gender_preference(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    aliases = {
        "man": "male",
        "men": "male",
        "male": "male",
        "woman": "female",
        "women": "female",
        "female": "female",
        "non-binary": "nonbinary",
        "nonbinary": "nonbinary",
        "non binary": "nonbinary",
    }
    return aliases.get(value, value)


def retrieve_candidates(
    db: Session,
    query_embedding: list[float],
    k: int = RETRIEVAL_SHORTLIST_SIZE,
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> list[tuple[Candidate, float]]:
    """Return the closest eligible candidates, closest first.

    Gender and age are hard filters from Basic Preferences. Vector similarity
    only ranks candidates *inside* those constraints and is never displayed.
    """
    query = db.query(Candidate, Candidate.embedding.cosine_distance(query_embedding).label("distance"))

    gender = _normalise_gender_preference(gender_preference)
    if gender and gender not in {"any", "all", "everyone"}:
        query = query.filter(Candidate.gender == gender)
    if age_min is not None:
        query = query.filter(Candidate.age >= age_min)
    if age_max is not None:
        query = query.filter(Candidate.age <= age_max)

    rows = query.order_by("distance").limit(k).all()
    return [(candidate, max(0.0, min(1.0, 1.0 - distance))) for candidate, distance in rows]


def shared_signals(user_ideal_partner_signals: list[BlueprintSignal], candidate_signals: list[dict]) -> list[str]:
    user_labels = {s.label.strip().lower(): s.label for s in user_ideal_partner_signals}
    candidate_labels = _signal_labels(candidate_signals)
    return [user_labels[label] for label in candidate_labels if label in user_labels]


def judge_and_explain_candidates(
    user_narrative: str, candidates: list[tuple[Candidate, list[str]]]
) -> dict[str, tuple[bool, list[MatchSection]]]:
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


def find_matches(
    db: Session,
    user_narrative: str,
    user_ideal_partner_signals: list[BlueprintSignal],
    gender_preference: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
) -> list[MatchOut]:
    query_text = _embedding_text(user_narrative or "", [s.label for s in user_ideal_partner_signals])
    query_embedding = embed_text(query_text)
    retrieved = retrieve_candidates(
        db,
        query_embedding,
        k=RETRIEVAL_SHORTLIST_SIZE,
        gender_preference=gender_preference,
        age_min=age_min,
        age_max=age_max,
    )

    candidates_with_shared = [
        (candidate, shared_signals(user_ideal_partner_signals, candidate.signals or []))
        for candidate, _similarity in retrieved
    ]
    judged = judge_and_explain_candidates(user_narrative or "", candidates_with_shared)

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
