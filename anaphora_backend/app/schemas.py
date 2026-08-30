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
    categories_covered: list[str]


class ConversationTurnResult(BaseModel):
    """Target schema for the conversational LLM's structured output — one
    call returns both its natural reply AND its own judgment of which base
    categories (BASE_CATEGORIES in conversation_chain.py) are now covered
    by the conversation so far, so the completion gate doesn't need a
    second LLM call to track coverage turn by turn."""
    reply: str = Field(description="The natural, conversational reply — one or two sentences, then the next question")
    categories_covered: list[str] = Field(
        description="Which of the base categories (personality, lifestyle, physical_type, "
        "relationship_dynamic, love_language, dealbreakers, about_you) have enough "
        "information so far, judged over the WHOLE conversation, not just this turn"
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


class DiscoveryResponseIn(BaseModel):
    user_id: str
    question_id: str
    response: str


class DiscoveryResultResponse(BaseModel):
    insight_text: str
    new_signals: list[BlueprintSignalOut]
    readiness_pct: int
