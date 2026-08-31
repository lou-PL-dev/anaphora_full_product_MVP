"""Central registry for every implemented Anaphora Discovery."""
from dataclasses import dataclass
from typing import Callable

from .schemas import SignalItem
from .chains.discovery_chain import (
    DISCOVERY_ID as LIFE_ID,
    DISCOVERY_TITLE as LIFE_TITLE,
    QUESTIONS as LIFE_QUESTIONS,
    synthesize_insight as synthesize_life_insight,
    responses_to_signals as life_responses_to_signals,
)
from .chains.discovery_library import DISCOVERY_DEFINITIONS, make_signal_mapper, make_synthesizer


@dataclass(frozen=True)
class DiscoverySpec:
    id: str
    title: str
    questions: list[dict]
    synthesize_insight: Callable[[dict[str, str]], str]
    responses_to_signals: Callable[[dict[str, str]], list[SignalItem]]
    perspective: str = "ME"
    category: str = "lifestyle"
    status: str = "active"


# Keep the original life Discovery implementation intact, while making its
# one choice question as open-ended as the rest of the library.
_life_questions = []
for q in LIFE_QUESTIONS:
    copy = dict(q)
    if copy.get("options"):
        copy["options"] = list(copy["options"]) + [{"id": "other", "label": "Something else"}]
    _life_questions.append(copy)

DISCOVERIES: dict[str, DiscoverySpec] = {
    LIFE_ID: DiscoverySpec(
        id=LIFE_ID,
        title=LIFE_TITLE,
        questions=_life_questions,
        synthesize_insight=synthesize_life_insight,
        responses_to_signals=life_responses_to_signals,
        perspective="ME",
        category="lifestyle",
    ),
}

for discovery_id, definition in DISCOVERY_DEFINITIONS.items():
    DISCOVERIES[discovery_id] = DiscoverySpec(
        id=discovery_id,
        title=definition["title"],
        questions=definition["questions"],
        synthesize_insight=make_synthesizer(definition["title"], definition["focus"]),
        responses_to_signals=make_signal_mapper(definition["questions"]),
        perspective="ME",
        category=definition["category"],
    )


def get_discovery_spec(discovery_id: str) -> DiscoverySpec | None:
    return DISCOVERIES.get(discovery_id)
