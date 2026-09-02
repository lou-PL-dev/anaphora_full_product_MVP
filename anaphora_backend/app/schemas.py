"""
Pydantic schemas.
- API request/response shapes for the routers.
- ExtractionResult is the schema LangChain's structured output targets for
  Operation B (PRD section 31) — its shape follows the PRD's own JSON
  example directly.
"""
from datetime import datetime
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


class ConversationObservation(BaseModel):
    perspective: str = Field(description="ME or IDEAL_PARTNER")
    category: BaseCategory
    label: str = Field(description="Short normalized human-readable meaning")
    strength: Strength = Strength.preference
    evidence_text: Optional[str] = Field(default=None)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explicit: bool = True


class LongInputChunkDigest(BaseModel):
    key_points: list[str] = Field(default_factory=list)
    coverage_fields: list[CoverageField] = Field(default_factory=list)
    evidence_snippets: list[str] = Field(default_factory=list)
    observations: list[ConversationObservation] = Field(default_factory=list)


class SignalItem(BaseModel):
    label: str
    strength: Strength = Strength.preference
    evidence_text: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explicit: bool = True


class PerspectiveBlueprint(BaseModel):
    personality: list[SignalItem] = []
    lifestyle: list[SignalItem] = []
    physical_type: list[SignalItem] = []
    relationship_dynamic: list[SignalItem] = []
    love_language: list[SignalItem] = []
    dealbreakers: list[SignalItem] = []
    values: list[SignalItem] = []


class ExtractionResult(BaseModel):
    ideal_partner: PerspectiveBlueprint
    me: PerspectiveBlueprint
    narrative: str


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
    key_points_just_shared: list[str]
    observations: list[ConversationObservation] = Field(default_factory=list)
    coverage_fields: list[CoverageField]
    next_question_target: Optional[CoverageField] = None
    reply: str


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
    confidence: Optional[float] = None

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
    body: str = Field(description="One or two sentences, grounded ONLY in the supplied relationship evidence")


class MatchOut(BaseModel):
    candidate: CandidateOut
    fit: FitLevel
    sections: list[MatchSection]


class MatchListResponse(BaseModel):
    ready: bool
    readiness_pct: int
    matches: list[MatchOut]


class MatchExplanation(BaseModel):
    candidate_id: str
    has_genuine_match: bool = Field(
        description="False when the relationship-level evidence does not justify an introduction"
    )
    recommended_fit: Optional[FitLevel] = Field(
        default=None,
        description="Qualitative relationship verdict. Null whenever has_genuine_match is false.",
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


class FriendInviteCreateResponse(BaseModel):
    token: str
    invite_count: int
    invite_limit: int


class FriendInviteInfo(BaseModel):
    questions: list[dict]


class FriendQuestionAnswer(BaseModel):
    question_id: str
    response: str = Field(min_length=1)


class FriendRespondRequest(BaseModel):
    friend_name: str = Field(min_length=1, max_length=60)
    answers: list[FriendQuestionAnswer]


class FriendExtractionResult(BaseModel):
    narrative: str = Field(description="A short paraphrase — never a verbatim quote from the friend")
    observations: list[ConversationObservation] = Field(default_factory=list)


class FriendSignalOut(BaseModel):
    id: str
    perspective: str
    category: str
    label: str
    strength: str
    evidence_text: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class FriendInviteListItem(BaseModel):
    id: str
    status: str  # pending | answered
    friend_name: Optional[str] = None
    reviewed: bool = False
    created_at: datetime


class FriendReviewOut(BaseModel):
    invite_id: str
    friend_name: str
    narrative: str
    signals: list[FriendSignalOut]


class FriendCommitRequest(BaseModel):
    accepted_signal_ids: list[str] = Field(default_factory=list)


class FriendCommitResponse(BaseModel):
    added_signals: list[BlueprintSignalOut]
    readiness_pct: int
