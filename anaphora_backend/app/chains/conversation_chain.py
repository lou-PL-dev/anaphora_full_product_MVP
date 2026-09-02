"""ME / YOU / US conversation orchestration with cumulative state."""
from collections import Counter

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import settings
from ..llm import get_chat_llm
from ..schemas import CoverageField, ConversationObservation, ConversationTurnResult

ME_FIELDS = {"personality", "lifestyle", "relationship_behavior", "core_values"}
IDEAL_FIELDS = {"personality", "lifestyle", "physical_type"}
US_FIELDS = {"relationship_shape", "connection_affection", "shared_direction", "boundaries"}

SYSTEM_PROMPT = """You are Anaphora, a warm, perceptive AI matchmaker. Learn a Relationship Blueprint through three distinct lenses:

- ME — who the user is independently: personality, current lifestyle, relationship_behavior (what they personally do in love or conflict), and core_values.
- IDEAL_PARTNER — qualities of the person they want: personality, lifestyle, and physical_type. Physical attraction matters and may include build, face, style, voice, presence or energy.
- US — what the relationship should create: relationship_shape (equality, commitment, autonomy, roles, decisions, time together), connection_affection (care, intimacy and feeling loved), shared_direction (future, family, home, money and important alignment), and boundaries.

Classification rule:
- "I am / I do" -> ME.
- "I want someone who is / does" -> IDEAL_PARTNER.
- "I want us / the relationship to" -> US.
One statement may support multiple fields when it genuinely contains multiple meanings. Reuse evidence rather than asking another question merely to fill a neighbouring category.

For every turn:
1. Extract atomic observations from the latest user message only.
2. Preserve all application-provided coverage; add every newly supported field.
3. Ask exactly one concise question about a genuinely missing field on the weakest lens.
4. Briefly reflect something specific the user just said before the question.

User-facing language rules:
- Never say "relationship dynamics", "values", "physical attributes", "love language", "category", "perspective", "ME / YOU / US", or expose the taxonomy.
- Ask in ordinary language through concrete behaviours, situations or examples.
- A physical-attraction question should normalize any answer, including no fixed type.
- Distinguish what the user wants from how the user personally behaves.
- If the user says a question was already asked, acknowledge it briefly and move to a clearly different subject.
- Do not ask a covered target again. A thin answer permits at most one concrete follow-up before moving on.
- Do not force daily contact, cohabitation, monogamy, children or conventional roles as assumptions.
- Never invent facts. Keep the tone natural, curious and concise.

When all three lenses have enough useful depth, next_question_target may be null and the reply can offer to create a first Blueprint."""

MINIMUM_USER_TURNS = 4
MAXIMUM_USER_TURNS = 16


def _message_content_for_model(message: dict) -> str:
    return message.get("processing_summary") or message.get("content", "")


def _to_langchain_messages(history: list[dict]) -> list:
    messages = []
    for message in history:
        content = _message_content_for_model(message)
        messages.append(HumanMessage(content=content) if message["role"] == "user" else AIMessage(content=content))
    return messages


def _field_for_observation(observation: ConversationObservation) -> CoverageField | None:
    prefix = {"ME": "me", "IDEAL_PARTNER": "ideal_partner", "US": "us"}.get(observation.perspective)
    if not prefix:
        return None
    try:
        return CoverageField(f"{prefix}_{observation.category.value}")
    except ValueError:
        return None


def accumulated_state(history: list[dict]) -> tuple[set[CoverageField], Counter]:
    covered: set[CoverageField] = set()
    asked: Counter = Counter()
    for message in history:
        if message.get("role") == "user":
            for raw in message.get("observations") or []:
                try:
                    field = _field_for_observation(ConversationObservation.model_validate(raw))
                except ValueError:
                    # A conversation started before the ME / YOU / US migration
                    # may still contain one legacy observation in its JSON.
                    continue
                if field:
                    covered.add(field)
        elif message.get("question_target"):
            try:
                asked[CoverageField(message["question_target"])] += 1
            except ValueError:
                pass
    return covered, asked


def _coverage_note(history, known_me, known_ideal, known_us):
    covered, asked = accumulated_state(history)
    for prefix, categories in (("me", known_me), ("ideal_partner", known_ideal), ("us", known_us)):
        for category in categories:
            try:
                covered.add(CoverageField(f"{prefix}_{category}"))
            except ValueError:
                pass
    covered_text = ", ".join(sorted(field.value for field in covered)) or "none"
    asked_text = ", ".join(f"{field.value} ({count}x)" for field, count in sorted(asked.items(), key=lambda item: item[0].value)) or "none"
    note = f"""

AUTHORITATIVE APPLICATION STATE
- Covered fields (never re-ask): {covered_text}
- Previously asked targets: {asked_text}
Use this state as authoritative. Do not infer that a covered field became missing. A target asked twice is forbidden even if its answer stayed thin."""
    return note, covered, asked


def converse(history, known_me=frozenset(), known_ideal=frozenset(), known_us=frozenset()):
    note, prior_coverage, asked = _coverage_note(history, known_me, known_ideal, known_us)
    llm = get_chat_llm(settings.openai_conversation_model, temperature=0.2)
    structured_llm = llm.with_structured_output(ConversationTurnResult)
    messages = [SystemMessage(content=SYSTEM_PROMPT + note)] + _to_langchain_messages(history)
    result = structured_llm.invoke(messages)

    new_fields = {_field_for_observation(obs) for obs in result.observations}
    result.coverage_fields = sorted(prior_coverage | {field for field in new_fields if field}, key=lambda field: field.value)

    if result.next_question_target in prior_coverage or asked[result.next_question_target] >= 2:
        forbidden = sorted(
            {field.value for field in prior_coverage} |
            {field.value for field, count in asked.items() if count >= 2}
        )
        messages.append(SystemMessage(content=(
            "Your proposed question repeats an already-covered or exhausted target. "
            f"Forbidden targets: {', '.join(forbidden)}. Choose a clearly different missing target and rewrite the reply."
        )))
        result = structured_llm.invoke(messages)
        new_fields = {_field_for_observation(obs) for obs in result.observations}
        result.coverage_fields = sorted(prior_coverage | {field for field in new_fields if field}, key=lambda field: field.value)
    return result


def user_turn_count(history):
    return sum(1 for message in history if message["role"] == "user")


def _categories(coverage_fields, prefix):
    marker = prefix + "_"
    return {field.value[len(marker):] for field in coverage_fields if field.value.startswith(marker)}


def lenses_ready(me, ideal, us):
    me_ready = {"personality", "lifestyle"}.issubset(me) and len(me & ME_FIELDS) >= 3
    ideal_ready = IDEAL_FIELDS.issubset(ideal)
    us_ready = "relationship_shape" in us and len(us & US_FIELDS) >= 3
    return me_ready and ideal_ready and us_ready


def is_ready_to_complete(history, coverage_fields):
    turns = user_turn_count(history)
    if turns < MINIMUM_USER_TURNS:
        return False
    return lenses_ready(
        _categories(coverage_fields, "me"),
        _categories(coverage_fields, "ideal_partner"),
        _categories(coverage_fields, "us"),
    ) or turns >= MAXIMUM_USER_TURNS
