"""
Pydantic schemas.
- API request/response shapes for the routers.
- ExtractionResult is the schema LangChain's structured output targets for
  Operation B — ME and IDEAL_PARTNER deliberately share one vocabulary.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Strength(str, Enum):
    hard_requirement = "hard_requirement"
    strong_preference = "strong_preference"
    preference = "preference"
    unknown = "unknown"


class CoreCategory(str, Enum):
    """Shared Blueprint dimensions for both ME and IDEAL_PARTNER."""
    personality = "personality"
    lifestyle = "lifestyle"
    physical_type = "physical_type"
    relationship_dynamic = "relationship_dynamic"
    love_language = "love_language"
    dealbreakers = "dealbreakers"
    values = "values"


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
    """Target schema for the LLM's structured extraction output."""
    ideal_partner: PerspectiveBlueprint
    me: PerspectiveBlueprint
    narrative: str = Field(
        description="A flowing, human-readable portrait of the ideal partner — "
        "written the way a perceptive friend would describe someone, in the "
        "same language the user spoke in — not a bullet list."
    )


class ConversationCoverage(BaseModel):
    """Coverage observed in the natural conversation, kept symmetric so the
    steering layer can notice what the user has revealed about themselves as
    well as what they want without collapsing ME into a generic about_you box."""
    me: list[CoreCategory] = Field(default_factory=list)
    ideal_partner: list[CoreCategory] = Field(default_factory=list)


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
    coverage: ConversationCoverage


class ConversationTurnResult(BaseModel):
    key_points_just_shared: list[str] = Field(
        description="Short phrases capturing what the user's LATEST message actually revealed"
    )
    coverage: ConversationCoverage = Field(
        description="Core categories with concrete information so far for BOTH ME and IDEAL_PARTNER, judged over the whole conversation"
    )
    reply: str = Field(
        description="Natural reply: briefly mirror what was shared, then ask one useful next question"
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
    ready: bool = Field(description="Whether matching readiness has reached 100")
    readiness_pct: int
    matches: list[MatchOut]


class MatchExplanation(BaseModel):
    candidate_id: str
    has_genuine_match: bool = Field(
        description="False if there is nothing specific and genuinely grounded to say about this candidate"
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
