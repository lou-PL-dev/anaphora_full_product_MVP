"""
Exercises the full PRD section 37 demo scenario end-to-end against a real
SQLite DB, with the three LLM call sites monkeypatched so it runs without
network access. Run: python test_flow.py
"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.schemas import (ConversationTurnResult, CoverageField, ExtractionResult,
                         PerspectiveBlueprint, IdealPartnerBlueprint, RelationshipBlueprint,
                         SignalItem, Strength)
from canonical_test_support import canonicalize_without_llm

FAKE_EXTRACTION = ExtractionResult(
    ideal_partner=IdealPartnerBlueprint(
        personality=[SignalItem(label="Warm", strength=Strength.strong_preference, evidence_text="warm and funny")],
        physical_type=[SignalItem(label="Dry humour", strength=Strength.preference, evidence_text="dry humour")],
    ),
    me=PerspectiveBlueprint(
        relationship_behavior=[SignalItem(label="Values presence over drama", strength=Strength.preference,
                                          evidence_text="doesn't make everything dramatic")],
    ),
    us=RelationshipBlueprint(
        connection_affection=[SignalItem(label="Emotionally communicative", strength=Strength.hard_requirement,
                                          evidence_text="need someone who can actually talk about things")],
    ),
    narrative="Warm, funny, someone who can actually talk about things without making everything dramatic.",
)

FAKE_TURN = ConversationTurnResult(
    key_points_just_shared=["warm", "funny"],
    coverage_fields=[CoverageField.ideal_partner_personality],
    reply="What kind of humour really works for you?",
)

with patch("app.routers.conversation_router.converse", return_value=FAKE_TURN), \
     patch("app.routers.conversation_router.extract_blueprint", return_value=FAKE_EXTRACTION), \
     patch("app.blueprint_canonicalizer.canonicalize_evidence", side_effect=canonicalize_without_llm):

    from app.main import app
    client = TestClient(app)
    headers = {"X-Anaphora-User-Id": "test-user-louise"}

    print("--- health ---")
    r = client.get("/health"); print(r.status_code, r.json())

    print("--- start conversation ---")
    r = client.post("/conversation/start", headers=headers)
    print(r.status_code, r.json())
    convo_id = r.json()["conversation_id"]

    print("--- send 4 user turns ---")
    for msg in ["Someone funny and warm, a little older than me.",
                "Dry humour. Someone who can laugh at himself.",
                "Present. I need someone who can actually talk about things but doesn't make everything dramatic.",
                "Somewhere between settled and adventurous."]:
        r = client.post("/conversation/message", headers=headers,
                         json={"conversation_id": convo_id, "message": msg})
        print(r.status_code, r.json())

    print("--- complete conversation (runs extraction) ---")
    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id})
    print(r.status_code)
    import json as _json
    print(_json.dumps(r.json(), indent=2))

    print("--- get blueprint ---")
    r = client.get("/blueprint", headers=headers)
    print(r.status_code, len(r.json()["signals"]), "signals")

    print("--- readiness after conversation ---")
    r = client.get("/readiness", headers=headers)
    print(r.status_code, r.json())

    print("--- get discovery ---")
    r = client.get("/discovery/life_you_are_building")
    print(r.status_code, r.json()["title"])

    print("--- respond to discovery ---")
    with patch("app.chains.discovery_chain.get_chat_llm") as discovery_llm:
        discovery_llm.return_value.invoke.return_value.content = "You want strong roots without feeling stuck."
        r = client.post("/discovery/life_you_are_building/respond", headers=headers, json=[
            {"user_id": "test-user-louise", "question_id": "saturday_2032", "response": "c"},
            {"user_id": "test-user-louise", "question_id": "roots_freedom", "response": "Roots"},
        ])
    print(r.status_code)
    print(_json.dumps(r.json(), indent=2))

    print("--- readiness after discovery (should increase) ---")
    r = client.get("/readiness", headers=headers)
    print(r.status_code, r.json())

    print("--- correct a signal ---")
    signals = client.get("/blueprint", headers=headers).json()["signals"]
    sig_id = signals[0]["id"]
    r = client.patch(f"/blueprint/signal/{sig_id}", headers=headers, json={"label": "Corrected label"})
    print(r.status_code, r.json())

print("\nALL FLOWS COMPLETED")
