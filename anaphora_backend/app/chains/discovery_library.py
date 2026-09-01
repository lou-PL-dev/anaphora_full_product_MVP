from __future__ import annotations

from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import SignalItem, Strength


def _option(id_: str, label: str) -> dict:
    return {"id": id_, "label": label}


def _choice(id_: str, prompt: str, options: list[tuple[str, str]], signal_prefix: str) -> dict:
    return {
        "id": id_,
        "prompt": prompt,
        "options": [_option(k, v) for k, v in options] + [_option("other", "Something else")],
        "signal_prefix": signal_prefix,
    }


def _spectrum(id_: str, prompt: str, left: str, right: str, signal_prefix: str) -> dict:
    return {"id": id_, "prompt": prompt, "spectrum": [left, right], "signal_prefix": signal_prefix}


def _text(id_: str, prompt: str, signal_prefix: str, placeholder: str = "Write whatever comes to mind…") -> dict:
    return {"id": id_, "prompt": prompt, "text": True, "placeholder": placeholder, "signal_prefix": signal_prefix}


DISCOVERY_DEFINITIONS = {
    "feel_at_home": {
        "title": "What makes you feel at home?",
        "category": "love_language",
        "perspective": "IDEAL_PARTNER",
        "focus": "emotional needs, intimacy, autonomy, reassurance and communication",
        "questions": [
            _choice("bad_day", "You've had a horrible day. What would you most want your partner to do?", [
                ("hold_listen", "Hold me and listen"),
                ("solve", "Help me solve it"),
                ("laugh", "Make me laugh"),
                ("space", "Give me some space"),
                ("depends", "It depends — I'd want to explain"),
            ], "After a hard day"),
            _choice("busy_week", "You've barely seen each other all week. What sounds best?", [
                ("reconnect", "Cancel everything and reconnect"),
                ("together_then_own", "Dinner together, then our own things"),
                ("go_out", "Go out and do something fun"),
                ("quiet_security", "Knowing we're okay is enough, even without much time together"),
            ], "After time apart"),
            _choice("something_wrong", "Something is bothering you in the relationship. You'd rather your partner…", [
                ("notice_ask", "Notice and ask"),
                ("wait", "Give me time until I bring it up"),
                ("direct", "Be direct immediately"),
                ("light", "Keep things light until I'm ready"),
            ], "When something feels off"),
            _spectrum("known_room", "Which feels more like love?", "Being deeply known", "Being given room to be yourself", "Love feels like"),
        ],
    },
    "chemistry": {
        "title": "What creates chemistry?",
        "category": "physical_type",
        "perspective": "IDEAL_PARTNER",
        "focus": "attraction, personality energy, physical preferences and interpersonal chemistry",
        "questions": [
            _choice("party_attention", "At a party, who catches your attention first?", [
                ("funny", "The person making everyone laugh"),
                ("quiet_presence", "The quiet person with a strong presence"),
                ("warm_deep", "The warm person talking deeply with one person"),
                ("unusual", "The slightly unusual one doing their own thing"),
            ], "Who catches your eye"),
            _spectrum("gentle_intense", "Which tension feels more attractive?", "Gentle", "Intense", "Attraction energy"),
            _choice("energy", "What kind of energy pulls you in most?", [
                ("playful", "Playful"),
                ("grounded", "Grounded"),
                ("magnetic", "Magnetic"),
                ("unconventional", "Unconventional"),
                ("calm", "Calm"),
                ("adventurous", "Adventurous"),
            ], "Energy that draws you in"),
            _choice("chemistry_killer", "Someone is objectively attractive. What most quickly kills the chemistry?", [
                ("serious", "They take themselves too seriously"),
                ("flat", "They feel emotionally flat"),
                ("chaotic", "They feel chaotic"),
                ("predictable", "They're too predictable"),
                ("uncurious", "They don't seem curious about me"),
            ], "Chemistry disappears when"),
        ],
    },
    "how_you_love": {
        "title": "How do you love?",
        "category": "relationship_dynamic",
        "perspective": "ME",
        "focus": "communication, closeness, conflict and emotional dynamics",
        "questions": [
            _choice("distance", "Your partner has seemed distant for two days. What's your instinct?", [
                ("ask", "Ask directly what's going on"),
                ("space", "Give them space and wait"),
                ("warmth", "Become warmer and try to reconnect"),
                ("distract", "Distract myself and see if it passes"),
            ], "When connection feels uncertain"),
            _choice("argument", "You're annoyed after an argument. What helps most?", [
                ("resolve_now", "Resolve it now"),
                ("cool_down", "Cool down, then come back"),
                ("affection", "Physical affection first"),
                ("humour", "A little humour to break the tension"),
            ], "After conflict"),
            _choice("reassurance", "Your partner wants more reassurance than you naturally give. What feels most true?", [
                ("happy", "I'd happily give more"),
                ("ask", "I can, but I'd need them to ask clearly"),
                ("pressure", "I'd start feeling pressured"),
                ("depends", "It depends how much"),
            ], "Giving reassurance"),
            _choice("hardest", "What feels hardest in love?", [
                ("uncertainty", "Not knowing where I stand"),
                ("crowded", "Feeling crowded"),
                ("misunderstood", "Feeling misunderstood"),
                ("no_play", "Losing playfulness"),
                ("emotional_work", "Being the one carrying the emotional work"),
            ], "Hardest part of love"),
        ],
    },
    "live_together": {
        "title": "Could we actually live together?",
        "category": "lifestyle",
        "perspective": "ME",
        "focus": "everyday compatibility, routines, money, cleanliness, social life, travel, sleep, family and leisure",
        "questions": [
            _choice("messy_sunday", "It's Sunday morning and the flat is a mess. What happens?", [
                ("clean_first", "Clean first, relax after"),
                ("later", "We'll get to it eventually"),
                ("split", "Split the chores and get it done"),
                ("dont_notice", "Honestly, I barely notice"),
            ], "Home rhythm"),
            _choice("windfall", "You unexpectedly get €2,000. As a couple, your instinct is…", [
                ("save", "Save it"),
                ("trip", "Book a trip"),
                ("home", "Improve the home"),
                ("split", "Spend some, save some"),
                ("separate", "Our money stays mostly separate anyway"),
            ], "Money instinct"),
            _choice("friends_over", "Your partner invites six friends over tonight without much warning. Your reaction?", [
                ("amazing", "Amazing"),
                ("sometimes", "Fine occasionally"),
                ("ask_first", "Ask me first next time"),
                ("no", "Absolutely not 😅"),
            ], "Spontaneous social plans"),
            _choice("hardest_difference", "Which everyday difference would be hardest to live with?", [
                ("sleep", "Different sleep schedules"),
                ("cleanliness", "Different cleanliness standards"),
                ("spending", "Different spending habits"),
                ("social", "Very different social needs"),
                ("planning", "Different attitudes to planning"),
            ], "Everyday friction point"),
        ],
    },
    "non_negotiables": {
        "title": "What can't you compromise on?",
        "category": "dealbreakers",
        "perspective": "IDEAL_PARTNER",
        "focus": "non-negotiables, strong preferences and ideal-world preferences",
        "questions": [
            _choice("must_have", "If only one quality absolutely had to be there, which would you protect first?", [
                ("kindness", "Kindness"),
                ("availability", "Emotional availability"),
                ("chemistry", "Sexual chemistry"),
                ("humour", "Humour"),
                ("curiosity", "Intellectual curiosity"),
                ("reliability", "Reliability"),
                ("independence", "Independence"),
                ("values", "Similar values"),
            ], "Must-have"),
            _choice("reliable_adventurous", "Which would you rather explore?", [
                ("reliable", "Very reliable, but life together may be fairly predictable"),
                ("adventurous", "Exciting and spontaneous, but sometimes inconsistent"),
            ], "Reliability vs adventure"),
            _choice("warm_ambitious", "Which trade-off feels easier to live with?", [
                ("warm", "Very warm and available, but not especially ambitious"),
                ("ambitious", "Very driven and inspiring, but often short on time"),
            ], "Availability vs ambition"),
            _text("walk_away", "What, if anything, would genuinely make you walk away from an otherwise promising relationship?", "Walk-away boundary"),
        ],
    },
    "relationship_archaeology": {
        "title": "Relationship Archaeology",
        "category": "relationship_dynamic",
        "perspective": "ME",
        "focus": "patterns across previous relationships, framed as hypotheses rather than diagnoses",
        "questions": [
            _text("attracted", "Think about someone you were strongly drawn to. What pulled you in at the beginning?", "What has attracted you"),
            _text("difficult", "What became difficult later?", "What became difficult"),
            _text("missing", "What did you repeatedly wish they would give you that you weren't getting?", "What you missed"),
            _text("needed_from_you", "Looking back, what did they probably need more of from you?", "What partners may need from you"),
            _choice("today", "Which sentence feels closest today?", [
                ("similar_healthier", "I want something similar, but healthier"),
                ("different", "I'm drawn to something very different now"),
                ("figuring_out", "I'm still figuring out what the pattern was"),
                ("varied", "My relationships have actually been quite different"),
            ], "How you see the pattern today"),
        ],
    },
}


def make_synthesizer(title: str, focus: str):
    system = f"""You are Anaphora. The user completed the Discovery '{title}', focused on {focus}.
Write ONE short, warm, perceptive sentence under 24 words that reflects a real pattern in the answers.
Sound like a thoughtful friend, not a test result. Do not diagnose, label attachment styles, or overclaim.
For Relationship Archaeology especially, present any pattern as something worth exploring, not a conclusion."""

    def synthesize(responses: dict[str, str]) -> str:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0.6, api_key=settings.openai_api_key)
        answers_text = "\n".join(f"- {qid}: {answer}" for qid, answer in responses.items())
        result = llm.invoke([
            {"role": "system", "content": system},
            {"role": "user", "content": f"Their answers:\n{answers_text}"},
        ])
        return result.content.strip()

    return synthesize


def make_signal_mapper(questions: list[dict], strength: Strength = Strength.preference):
    by_id = {q["id"]: q for q in questions}

    def map_signals(responses: dict[str, str]) -> list[SignalItem]:
        signals: list[SignalItem] = []
        for qid, answer in responses.items():
            q = by_id.get(qid)
            if not q or not str(answer).strip():
                continue
            readable = str(answer).strip()
            for option in q.get("options", []):
                if option["id"] == answer:
                    readable = option["label"]
                    break
            prefix = q.get("signal_prefix", q.get("prompt", "Preference"))
            item_strength = Strength.hard_requirement if qid == "walk_away" and readable else strength
            signals.append(SignalItem(
                label=f"{prefix}: {readable}",
                strength=item_strength,
                evidence_text=f"{q.get('prompt', qid)} — {readable}",
            ))
        return signals

    return map_signals
