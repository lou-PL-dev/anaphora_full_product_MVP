"""A follow-up conversation ("Add more") should ADD to the Blueprint, not
erase categories an earlier conversation already established. Run:
python test_conversation_merge.py"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.schemas import ExtractionResult, PerspectiveBlueprint, SignalItem, Strength

FIRST_EXTRACTION = ExtractionResult(
    ideal_partner=PerspectiveBlueprint(
        personality=[SignalItem(label="Warm", strength=Strength.strong_preference, evidence_text="warm")],
    ),
    me=PerspectiveBlueprint(
        lifestyle=[SignalItem(label="Homebody", strength=Strength.preference, evidence_text="likes staying in")],
    ),
    narrative="Warm and drawn to quiet nights in.",
)

SECOND_EXTRACTION = ExtractionResult(
    ideal_partner=PerspectiveBlueprint(
        values=[SignalItem(label="Family-oriented", strength=Strength.preference, evidence_text="wants family closeness")],
    ),
    me=PerspectiveBlueprint(),
    narrative="Values close family ties.",
)

with patch("app.chains.extraction_chain.extract_blueprint", side_effect=[FIRST_EXTRACTION, SECOND_EXTRACTION]):
    from app.main import app
    client = TestClient(app)
    headers = {"X-Anaphora-User-Id": "merge-test-user"}

    r = client.post("/conversation/start", headers=headers)
    convo_id_1 = r.json()["conversation_id"]
    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id_1})
    print("--- 1st complete ---", r.status_code, len(r.json()["signals"]), "signals")

    signals = client.get("/blueprint", headers=headers).json()["signals"]
    categories = {(s["perspective"], s["category"]) for s in signals}
    assert categories == {("IDEAL_PARTNER", "personality"), ("ME", "lifestyle")}, categories
    print("after 1st conversation:", categories)

    r = client.post("/conversation/start", headers=headers)
    convo_id_2 = r.json()["conversation_id"]
    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id_2})
    print("--- 2nd complete (different category) ---", r.status_code, len(r.json()["signals"]), "signals")

    signals = client.get("/blueprint", headers=headers).json()["signals"]
    categories = {(s["perspective"], s["category"]) for s in signals}
    print("after 2nd conversation:", categories)
    assert categories == {
        ("IDEAL_PARTNER", "personality"), ("ME", "lifestyle"), ("IDEAL_PARTNER", "values"),
    }, f"expected the 1st conversation's categories to survive alongside the 2nd's, got {categories}"

    narrative = client.get("/blueprint", headers=headers).json()["narrative"]
    assert "Warm and drawn to quiet nights in." in narrative and "Values close family ties." in narrative, narrative
    print("narrative accumulated:", narrative)

print("\nMERGE BEHAVIOR VERIFIED — a follow-up conversation adds to the Blueprint instead of replacing it")
