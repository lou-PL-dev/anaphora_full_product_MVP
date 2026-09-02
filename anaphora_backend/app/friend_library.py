"""The fixed friend questionnaire (PRD section 19 — "Friend Questions").

Deliberately static and small: four lightweight questions, no AI
conversation stage (PRD section 20 is explicitly out of scope for this
pass). The friend already knows who invited them (they got the link
directly from that person) — the app never needs to know or show the
inviting user's name, so the questions are phrased generically ("them").
"""

FRIEND_QUESTIONS = [
    {
        "id": "brings_out_best",
        "prompt": "What kind of person brings out the best in them?",
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
        "prompt": "What do they think they want that you're not convinced they actually need?",
        "text": True,
        "placeholder": "Write whatever comes to mind…",
    },
    {
        "id": "past_relationship",
        "prompt": "Think about someone they dated who you weren't crazy about. What did you see that perhaps they didn't? (No names, please.)",
        "text": True,
        "placeholder": "Write whatever comes to mind…",
    },
    {
        "id": "worked_well",
        "prompt": "What have you seen work particularly well for them?",
        "text": True,
        "placeholder": "Write whatever comes to mind…",
    },
]

FRIEND_QUESTION_IDS = {q["id"] for q in FRIEND_QUESTIONS}


def question_prompt(question_id: str) -> str:
    for q in FRIEND_QUESTIONS:
        if q["id"] == question_id:
            return q["prompt"]
    return question_id
