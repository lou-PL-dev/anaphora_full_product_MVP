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


# --- LLM structured-extraction output (Operation B) -------------------------

class SignalItem(BaseModel):
    label: str = Field(description="Short human-readable label, e.g. 'Warm', 'Self-deprecating humour'")
    strength: Strength = Strength.preference
    evidence_text: Optional[str] = Field(
        default=None, description="Short phrase from the conversation that caused this extraction"
    )


class IdealPartnerBlueprint(BaseModel):
    personality: list[SignalItem] = []
    lifestyle: list[SignalItem] = []
    relationship_dynamic: list[SignalItem] = []
    attraction: list[SignalItem] = []
    values: list[SignalItem] = []
    dealbreakers: list[SignalItem] = []


class MeBlueprint(BaseModel):
    personality: list[SignalItem] = []
    lifestyle: list[SignalItem] = []
    relationship_style: list[SignalItem] = []
    values: list[SignalItem] = []


class ExtractionResult(BaseModel):
    """Target schema for the LLM's structured output — see chains/extraction.py"""
    ideal_partner: IdealPartnerBlueprint
    me: MeBlueprint


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
    readiness_pct: int


class SignalCorrectionRequest(BaseModel):
    label: Optional[str] = None
    strength: Optional[Strength] = None


class ReadinessResponse(BaseModel):
    readiness_pct: int
    breakdown: dict[str, dict]


class DiscoveryResponseIn(BaseModel):
    user_id: str
    question_id: str
    response: str


class DiscoveryResultResponse(BaseModel):
    insight_text: str
    new_signals: list[BlueprintSignalOut]
    readiness_pct: int
