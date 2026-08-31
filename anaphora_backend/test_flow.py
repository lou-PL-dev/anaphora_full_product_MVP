"""Manual end-to-end smoke harness. Run from anaphora_backend: python test_flow.py"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.schemas import ConversationTurnResult, ConversationCoverage, ExtractionResult, PerspectiveBlueprint, SignalItem, Strength

# Rich enough on both sides to satisfy the 30% ME + 30% IDEAL_PARTNER gates.
def side(prefix):
    return PerspectiveBlueprint(
        personality=[SignalItem(label=f"{prefix} personality")],
        lifestyle=[SignalItem(label=f"{prefix} lifestyle")],
        physical_type=[SignalItem(label=f"{prefix} physical")],
        relationship_dynamic=[SignalItem(label=f"{prefix} relationship")],
        values=[SignalItem(label=f"{prefix} values")],
    )

FAKE_EXTRACTION = ExtractionResult(
    ideal_partner=side("Ideal"),
    me=side("Me"),
    narrative="A grounded portrait of the person who could fit.",
)

FAKE_TURN = ConversationTurnResult(
    key_points_just_shared=["warm", "grounded"],
    coverage=ConversationCoverage(
        me=["personality", "lifestyle", "physical_type", "relationship_dynamic", "values"],
        ideal_partner=["personality", "lifestyle", "physical_type", "relationship_dynamic", "values"],
    ),
    reply="That gives me a real sense of both sides. What matters most in everyday connection?",
)

with patch("app.chains.conversation_chain.converse", return_value=FAKE_TURN), \
     patch("app.chains.extraction_chain.extract_blueprint", return_value=FAKE_EXTRACTION):
    from app.main import app
    client = TestClient(app)
    headers = {"X-Anaphora-User-Id": "test-user-louise"}

    assert client.get("/health").status_code == 200
    convo_id = client.post("/conversation/start", headers=headers).json()["conversation_id"]

    for msg in ["Someone warm.", "I am grounded too.", "We both need some independence."]:
        r = client.post("/conversation/message", headers=headers, json={"conversation_id": convo_id, "message": msg})
        assert r.status_code == 200

    r = client.post("/conversation/complete", headers=headers, json={"conversation_id": convo_id})
    assert r.status_code == 200
    # Conversation alone = both profile gates = 60%.
    assert r.json()["readiness_pct"] == 60

    # Persisting basic preferences adds 20%.
    r = client.patch("/profile/matching-preferences", headers=headers, json={
        "gender_preference": "Men", "preferred_age_range": "35-47"
    })
    assert r.status_code == 200
    assert r.json()["readiness_pct"] == 80

    print("SMOKE FLOW PASSED — 60% Blueprint + 20% preferences; Discovery completes the final gate.")
