"""
Pydantic schemas.
- API request/response shapes for the routers.
- ExtractionResult is the schema LangChain's structured output targets for
  Operation B (PRD section 31) — its shape follows the PRD's own JSON
  example directly.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Strength(str, Enum):
    hard_requirement = "hard_requirement"
    strong_preference = "strong_preference"
    preference = "preference"
    unknown = "unknown"


class BaseCategory(str, Enum):
    """The 7 base fields a Blueprint needs before a conversation can
    complete — see BASE_CATEGORIES / is_ready_to_complete in
    chains/conversation_chain.py. A real Enum here (not a free-text list[str]
    with a description) matters: with_structured_output constrains the
    LLM's JSON schema to exactly these values, so a label typo or synonym
    can't silently fail to match and permanently block a category from
    ever counting as covered."""
    personality = "personality"
    lifestyle = "lifestyle"
    physical_type = "physical_type"
    relationship_dynamic = "relationship_dynamic"
    love_language = "love_language"
    dealbreakers = "dealbreakers"
    about_you = "about_you"


# --- LLM structured-extraction output (Operation B) -------------------------

# The same 7 categories apply to BOTH perspectives — what the user wants in
# an ideal partner, and what the user reveals about themselves. Six of
# these (everything but "values") are also the base fields the completion
# gate in conversation_chain.py requires be covered before a conversation
# can complete — see BASE_CATEGORIES there.
class SignalItem(BaseModel):
    label: str = Field(description="Short human-readable label, e.g. 'Warm', 'Self-deprecating humour'")
    strength: Strength = Strength.preference
    evidence_text: Optional[str] = Field(
        default=None, description="Short phrase from the conversation that caused this extraction"
    )


class PerspectiveBlueprint(BaseModel):
    personality: list[SignalItem] = []
    lifestyle: list[SignalItem] = []
    physical_type: list[SignalItem] = []
    relationship_dynamic: list[SignalItem] = []
    love_language: list[SignalItem] = []
    dealbreakers: list[SignalItem] = []
    values: list[SignalItem] = []


class ExtractionResult(BaseModel):
    """Target schema for the LLM's structured output — see chains/extraction.py"""
    ideal_partner: PerspectiveBlueprint
    me: PerspectiveBlueprint
    narrative: str = Field(
        description="A flowing, human-readable portrait of the ideal partner — "
        "written the way a perceptive friend would describe someone, in the "
        "same language the user spoke in — not a bullet list."
    )


# --- API request/response shapes --------------------------------------------

class ConversationStartResponse(BaseModel):
    conversation_id: str
    message: str


class ConversationMessageRequest(BaseModel):
    conversation_id: str
    message: str


class ConversationMessageResponse(BaseModel):
    reply: str
    turn_count: int
    ready_to_complete: bool
    categories_covered: list[BaseCategory]


class ConversationTurnResult(BaseModel):
    """Target schema for the conversational LLM's structured output — one
    call returns its own judgment of which base categories are now covered
    by the conversation so far AND its natural reply, so the completion
    gate doesn't need a second LLM call to track coverage turn by turn.

    Field ORDER here matters, not just presence: with_structured_output
    generates JSON fields sequentially in declaration order, so putting
    key_points_just_shared and categories_covered BEFORE reply forces the
    model to explicitly work out what was just said and what's already
    covered first — reply is then generated conditioned on that already-
    committed judgment, instead of being improvised from scratch with no
    coverage reasoning behind it (which produced generic non-mirroring
    replies and re-asking about already-covered ground when reply was
    generated first, before any coverage judgment existed to steer it)."""
    key_points_just_shared: list[str] = Field(
        description="Short phrases capturing what the user's LATEST message actually revealed — "
        "used to ground a real mirror-back in the reply, not a generic acknowledgment"
    )
    categories_covered: list[BaseCategory] = Field(
        description="Which base categories have enough information so far, judged "
        "over the WHOLE conversation, not just this turn"
    )
    reply: str = Field(
        description="The natural, conversational reply — briefly mirror back key_points_just_shared, "
        "then ask about a category NOT in categories_covered, one or two sentences total"
    )


class ConversationCompleteRequest(BaseModel):
    conversation_id: str


class BlueprintSignalOut(BaseModel):
    id: str
    perspective: str
    category: str
    label: str
    strength: str
    source: str
    evidence_text: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationCompleteResponse(BaseModel):
    signals: list[BlueprintSignalOut]
    narrative: str
    readiness_pct: int


class BlueprintResponse(BaseModel):
    signals: list[BlueprintSignalOut]
    narrative: Optional[str] = None


class SignalCorrectionRequest(BaseModel):
    label: Optional[str] = None
    strength: Optional[Strength] = None


class ReadinessResponse(BaseModel):
    readiness_pct: int
    breakdown: dict[str, dict]


class CandidateOut(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    photo_url: Optional[str] = None
    narrative: str

    class Config:
        from_attributes = True


class FitLevel(str, Enum):
    """PRD section 26 (Match Presentation): 'Anaphora deliberately avoids
    presenting 92% compatible. Instead: Strong fit / Worth exploring.' No
    numeric score is ever shown — this is the only signal of match strength
    the frontend renders, and it's a RELATIVE ranking within a single
    /matches response (the best candidate that passed the genuineness
    filter), not a claim about any absolute, comparable-across-requests
    score."""
    strong_fit = "strong_fit"
    worth_exploring = "worth_exploring"


class MatchSection(BaseModel):
    """One themed paragraph in Anaphora's 'why this match' style — PRD
    section 26's own example headings are 'The life you're building', 'How
    you connect', 'Something you might enjoy', and (for an honest tension)
    'Something to explore'. The model isn't restricted to exactly those
    strings, but should stay in that register."""
    heading: str
    body: str = Field(description="One or two sentences, grounded ONLY in the information given — never invented")


class MatchOut(BaseModel):
    candidate: CandidateOut
    fit: FitLevel
    sections: list[MatchSection] = Field(
        description="1-4 themed paragraphs explaining the match — never empty: a candidate with "
        "nothing genuine to say is dropped before reaching this response entirely, per PRD section 26"
    )


class MatchListResponse(BaseModel):
    ready: bool = Field(description="Whether readiness_pct has reached 100 — matching is only offered once a Blueprint is complete")
    readiness_pct: int
    matches: list[MatchOut] = Field(
        description="Empty either because ready is False, or because ready is True but nothing in the "
        "candidate pool currently clears the genuineness bar — the frontend distinguishes those two "
        "cases via `ready`, not by matches being empty alone"
    )


# --- LLM structured output for the matching chain's generation step --------

class MatchExplanation(BaseModel):
    candidate_id: str
    has_genuine_match: bool = Field(
        description="False if there is nothing specific and genuinely grounded to say about this "
        "candidate — a thin or generic overlap does NOT count as genuine. When false, sections MUST "
        "be empty; this candidate will not be shown to the user at all. It is not only acceptable but "
        "REQUIRED to say false rather than stretch a vague signal into a confident-sounding paragraph."
    )
    sections: list[MatchSection] = Field(
        default_factory=list,
        description="1-4 sections when has_genuine_match is true; empty when it's false",
    )


class MatchExplanationsResult(BaseModel):
    """Target schema for the matching chain's generation call — one LLM call
    judges AND explains all retrieved candidates at once, same cost-conscious
    pattern as conversation_chain.converse() returning reply +
    categories_covered together."""
    explanations: list[MatchExplanation]


class DiscoveryResponseIn(BaseModel):
    user_id: str
    question_id: str
    response: str


class DiscoveryResultResponse(BaseModel):
    insight_text: str
    new_signals: list[BlueprintSignalOut]
    readiness_pct: int
