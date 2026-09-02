"""The fixed friend questionnaire (PRD section 19 — "Friend Questions").

Deliberately static and small: four lightweight questions, no AI
conversation stage (PRD section 20 is explicitly out of scope for this
pass). Prompts use {name} so callers can substitute the inviting user's
first name before sending them to the friend.
"""

FRIEND_QUESTIONS = [
    {
        "id": "brings_out_best",
        "prompt": "What kind of person brings out the best in {name}?",
        "options": [
            {"id": "grounding", "label": "Someone grounding"},
            {"id": "adventurous", "label": "Someone adventurous"},
            {"id": "intellectual", "label": "Someone intellectually challenging"},
            {"id": "affectionate", "label": "Someone affectionate"},
            {"id": "independent", "label": "Someone independent"},
            {"id": "other", "label": "Something else"},
        ],
    },
    {
        "id": "wants_vs_needs",
        "prompt": "What does {name} think they want that you're not convinced they actually need?",
        "text": True,
        "placeholder": "Write whatever comes to mind…",
    },
    {
        "id": "past_relationship",
        "prompt": "Think about someone {name} dated who you weren't crazy about. What did you see that perhaps they didn't? (No names, please.)",
        "text": True,
        "placeholder": "Write whatever comes to mind…",
    },
    {
        "id": "worked_well",
        "prompt": "What have you seen work particularly well for {name}?",
        "text": True,
        "placeholder": "Write whatever comes to mind…",
    },
]

FRIEND_QUESTION_IDS = {q["id"] for q in FRIEND_QUESTIONS}


def formatted_questions(name: str) -> list[dict]:
    out = []
    for q in FRIEND_QUESTIONS:
        copy = dict(q)
        copy["prompt"] = q["prompt"].format(name=name)
        out.append(copy)
    return out


def question_prompt(question_id: str, name: str) -> str:
    for q in FRIEND_QUESTIONS:
        if q["id"] == question_id:
            return q["prompt"].format(name=name)
    return question_id
