"""Central registry for every implemented Anaphora Discovery.

Adding a Discovery should require two things only:
1. implement its questions + synthesis/signal mapping in app/chains/;
2. register one DiscoverySpec below.

The same registry powers both API lookup and database seeding, so a
Discovery cannot be available in code while missing from the `discoveries`
table (the production bug this module is designed to prevent).
"""
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


DISCOVERIES: dict[str, DiscoverySpec] = {
    LIFE_ID: DiscoverySpec(
        id=LIFE_ID,
        title=LIFE_TITLE,
        questions=LIFE_QUESTIONS,
        synthesize_insight=synthesize_life_insight,
        responses_to_signals=life_responses_to_signals,
        perspective="ME",
        category="lifestyle",
    ),
}


def get_discovery_spec(discovery_id: str) -> DiscoverySpec | None:
    return DISCOVERIES.get(discovery_id)
