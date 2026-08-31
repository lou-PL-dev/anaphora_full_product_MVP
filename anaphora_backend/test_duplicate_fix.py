"""Reproduces the exact bug: calling /conversation/complete more than once
should NOT duplicate signals, and should now be blocked outright."""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.schemas import ConversationTurnResult, ExtractionResult, PerspectiveBlueprint, SignalItem, Strength

FAKE_EXTRACTION = ExtractionResult(
    ideal_partner=PerspectiveBlueprint(
        personality=[SignalItem(label="Warm", strength=Strength.strong_preference, evidence_text="warm")],
    ),
    me=PerspectiveBlueprint(),
    narrative="Warm.",
)

FAKE_TURN = ConversationTurnResult(
    key_points_just_shared=["warm"], categories_covered=["personality"], reply="Tell me more?"
)

with patch("app.chains.conversation_chain.converse", return_value=FAKE_TURN), \
     patch("app.chains.extraction_chain.extract_blueprint", return_value=FAKE_EXTRACTION):

    from app.main import app
    client = TestClient(app)
    headers = {"X-Anaphora-User-Id": "dup-test-user"}

    r = client.post("/conversation/start", headers=headers)
    convo_id = r.json()["conversation_id"]
    for _ in range(4):
        client.post("/conversation/message", headers=headers,
                     json={"conversation_id": convo_id, "message": "something"})

    print("--- first /complete call ---")
    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id})
    print(r.status_code, len(r.json()["signals"]), "signals returned")

    print("--- blueprint after 1st complete ---")
    signals = client.get("/blueprint", headers=headers).json()["signals"]
    print(len(signals), "total signals in DB")
    assert len(signals) == 1, f"expected 1 signal, got {len(signals)}"

    print("--- second /complete call on SAME conversation (should be blocked) ---")
    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id})
    print(r.status_code, r.json())
    assert r.status_code == 400, "expected 400, conversation already completed"

    print("--- start a NEW conversation and complete it too (should REPLACE, not duplicate) ---")
    r = client.post("/conversation/start", headers=headers)
    convo_id_2 = r.json()["conversation_id"]
    for _ in range(4):
        client.post("/conversation/message", headers=headers,
                     json={"conversation_id": convo_id_2, "message": "something else"})
    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id_2})
    print(r.status_code, len(r.json()["signals"]), "signals returned")

    signals = client.get("/blueprint", headers=headers).json()["signals"]
    print(len(signals), "total signals in DB after 2nd conversation")
    assert len(signals) == 1, f"expected still 1 signal (replaced, not appended), got {len(signals)}"

print("\nBUG FIX VERIFIED — no duplication, re-completion blocked, new conversation replaces cleanly")
