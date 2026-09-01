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
    personality = "personality"
    lifestyle = "lifestyle"
    physical_type = "physical_type"
    relationship_dynamic = "relationship_dynamic"
    love_language = "love_language"
    dealbreakers = "dealbreakers"
    values = "values"


class CoverageField(str, Enum):
    """Conversation coverage is perspective-specific.

    A flat category list cannot distinguish learning that the ideal partner
    is adventurous from learning that the user is adventurous. These explicit
    fields make the steering model keep filling both sides of the Blueprint.
    """
    ideal_partner_personality = "ideal_partner_personality"
    ideal_partner_lifestyle = "ideal_partner_lifestyle"
    ideal_partner_physical_type = "ideal_partner_physical_type"
    ideal_partner_relationship_dynamic = "ideal_partner_relationship_dynamic"
    ideal_partner_love_language = "ideal_partner_love_language"
    ideal_partner_dealbreakers = "ideal_partner_dealbreakers"
    ideal_partner_values = "ideal_partner_values"
    me_personality = "me_personality"
    me_lifestyle = "me_lifestyle"
    me_physical_type = "me_physical_type"
    me_relationship_dynamic = "me_relationship_dynamic"
    me_love_language = "me_love_language"
    me_dealbreakers = "me_dealbreakers"
    me_values = "me_values"


class LongInputChunkDigest(BaseModel):
    """Compact, evidence-preserving understanding of one internal chunk.

    This is processing memory only: the original user message remains stored
    verbatim and still counts as one conversation turn.
    """
    key_points: list[str] = Field(
        default_factory=list,
        description="Specific factual points from this chunk, preserving nuance and contradictions",
    )
    coverage_fields: list[CoverageField] = Field(
        default_factory=list,
        description="Perspective-specific Blueprint fields genuinely supported by this chunk",
    )
    evidence_snippets: list[str] = Field(
        default_factory=list,
        description="A few short verbatim snippets worth retaining for grounding and conversational tone",
    )


# --- LLM structured-extraction output (Operation B) -------------------------

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
    categories_covered: list[CoverageField]


class ConversationTurnResult(BaseModel):
    """One conversational LLM call returns coverage, steering target, and reply.

    Field order is intentional: the model must first understand the latest
    message, then recompute cumulative perspective-specific coverage, then
    choose a genuinely missing target before it writes the natural-language
    response.
    """
    key_points_just_shared: list[str] = Field(
        description="Short phrases capturing what the user's LATEST message actually revealed"
    )
    coverage_fields: list[CoverageField] = Field(
        description="ALL sufficiently covered ME and IDEAL_PARTNER fields across the WHOLE conversation"
    )
    next_question_target: Optional[CoverageField] = Field(
        default=None,
        description="One still-missing field the next question should explore. Null only when both perspectives have enough coverage to complete.",
    )
    reply: str = Field(
        description="Briefly mirror the latest specifics, then ask exactly one natural question aimed at next_question_target"
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
    """PRD section 26 (Match Presentation): qualitative fit only."""
    strong_fit = "strong_fit"
    worth_exploring = "worth_exploring"


class MatchSection(BaseModel):
    heading: str
    body: str = Field(description="One or two sentences, grounded ONLY in the information given — never invented")


class MatchOut(BaseModel):
    candidate: CandidateOut
    fit: FitLevel
    sections: list[MatchSection] = Field(
        description="1-4 themed paragraphs explaining the match — never empty"
    )


class MatchListResponse(BaseModel):
    ready: bool = Field(description="Whether readiness_pct has reached 100")
    readiness_pct: int
    matches: list[MatchOut]


class MatchExplanation(BaseModel):
    candidate_id: str
    has_genuine_match: bool = Field(
        description="False when there is nothing specific and genuinely grounded to say about this candidate"
    )
    sections: list[MatchSection] = Field(default_factory=list)


class MatchExplanationsResult(BaseModel):
    explanations: list[MatchExplanation]


class DiscoveryResponseIn(BaseModel):
    user_id: str
    question_id: str
    response: str


class DiscoveryResultResponse(BaseModel):
    insight_text: str
    new_signals: list[BlueprintSignalOut]
    readiness_pct: int
