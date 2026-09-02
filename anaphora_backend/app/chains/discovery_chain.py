"""
The one functional Discovery required for MVP (PRD section 4F):
"What kind of life are you building?"

Questions are fixed/hardcoded for MVP (PRD section 5 excludes a full
Discovery library). Responses are synthesized into a short personalised
insight (PRD section 37, e.g. "You want strong roots without feeling
stuck.") and mapped to lifestyle-category Blueprint signals.
"""
from ..llm import get_chat_llm
from ..schemas import SignalItem, Strength

DISCOVERY_ID = "life_you_are_building"
DISCOVERY_TITLE = "What kind of life are you building?"

QUESTIONS = [
    {
        "id": "saturday_2032",
        "prompt": "It's 2032. Which Saturday sounds better?",
        "options": [
            {"id": "a", "label": "Breakfast at home, kids running around, friends over later"},
            {"id": "b", "label": "Deciding spontaneously whether to take the train to Copenhagen"},
            {"id": "c", "label": "Slow morning, creative project, dinner with a few close friends"},
            {"id": "d", "label": "Hosting 20 people tonight"},
        ],
    },
    {
        "id": "roots_freedom",
        "prompt": "Which matters more to you?",
        "spectrum": ["Roots", "Freedom"],
    },
    {
        "id": "comfort_adventure",
        "prompt": "Which matters more to you?",
        "spectrum": ["Comfort", "Adventure"],
    },
    {
        "id": "togetherness_independence",
        "prompt": "Which matters more to you?",
        "spectrum": ["Togetherness", "Independence"],
    },
]

SYNTHESIS_SYSTEM_PROMPT = """You are Anaphora. A user just answered a short set of \
lifestyle trade-off questions about the kind of life they want to build. Write ONE short, \
warm, insightful sentence (under 20 words) that reflects a genuine pattern in their \
answers back to them — the way a perceptive friend would, not a generic personality-test \
result. Example tone: "You want strong roots without feeling stuck." Do not use clinical \
or diagnostic language."""


def synthesize_insight(responses: dict[str, str]) -> str:
    llm = get_chat_llm(temperature=0.6)
    answers_text = "\n".join(f"- {qid}: {answer}" for qid, answer in responses.items())
    result = llm.invoke([
        {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
        {"role": "user", "content": f"Their answers:\n{answers_text}"},
    ])
    return result.content.strip()


def responses_to_signals(responses: dict[str, str]) -> list[SignalItem]:
    """Simple deterministic mapping for MVP — richer inference can come later.
    Any spectrum answer becomes a lifestyle preference signal; the free
    Saturday-scenario choice becomes a lifestyle signal too."""
    signals = []
    label_map = {
        "a": "Home-oriented, family-centered",
        "b": "Spontaneous, adventurous",
        "c": "Balanced — quiet creativity with close friends",
        "d": "Highly social, energized by hosting",
    }
    if "saturday_2032" in responses:
        label = label_map.get(responses["saturday_2032"], responses["saturday_2032"])
        signals.append(SignalItem(label=label, strength=Strength.preference,
                                   evidence_text=f"Chose: {responses['saturday_2032']}"))
    for key in ("roots_freedom", "comfort_adventure", "togetherness_independence"):
        if key in responses:
            signals.append(SignalItem(
                label=f"Leans toward: {responses[key]}",
                strength=Strength.preference,
                evidence_text=f"{key}: {responses[key]}",
            ))
    return signals
