"""A follow-up conversation ("Add more") should know what's already covered
from earlier conversations/Discoveries — it shouldn't re-lead with
IDEAL_PARTNER when that side is already done, and it shouldn't judge
completion from its own empty transcript alone. Run:
python test_conversation_steering.py"""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.schemas import ConversationTurnResult, CoverageField

FAKE_TURN = ConversationTurnResult(
    key_points_just_shared=["works from home", "close with siblings"],
    coverage_fields=[
        CoverageField.me_personality, CoverageField.me_lifestyle, CoverageField.me_relationship_behavior,
        CoverageField.ideal_partner_personality, CoverageField.ideal_partner_lifestyle,
        CoverageField.ideal_partner_physical_type, CoverageField.us_relationship_shape,
        CoverageField.us_connection_affection, CoverageField.us_shared_direction,
    ],
    reply="Thanks for sharing that.",
)

with patch("app.routers.conversation_router.converse", return_value=FAKE_TURN):
    from app.main import app
    from app.database import SessionLocal
    from app.models import User, BlueprintSignal

    client = TestClient(app)
    headers = {"X-Anaphora-User-Id": "steering-test-user"}

    # Get the user created and pre-seed IDEAL_PARTNER as already fully covered
    # from an earlier conversation, leaving ME untouched.
    client.get("/health")
    db = SessionLocal()
    db.merge(User(id="steering-test-user"))
    db.commit()
    for category in ["personality", "lifestyle", "physical_type"]:
        db.add(BlueprintSignal(
            user_id="steering-test-user", perspective="IDEAL_PARTNER", category=category,
            label="x", strength="preference", source="conversation", evidence_text="x",
        ))
    db.commit()
    for category in ["relationship_shape", "connection_affection", "shared_direction"]:
        db.add(BlueprintSignal(
            user_id="steering-test-user", perspective="US", category=category,
            label="x", strength="preference", source="conversation", evidence_text="x",
        ))
    db.commit()
    db.close()

    r = client.post("/conversation/start", headers=headers)
    opening = r.json()["message"]
    print("Opening message:", opening)
    assert "about you" in opening.lower(), f"expected an ME-focused opener, got: {opening}"

    convo_id = r.json()["conversation_id"]
    last = None
    for i in range(4):
        last = client.post("/conversation/message", headers=headers,
                            json={"conversation_id": convo_id, "message": f"turn {i}"}).json()
    print("ready_to_complete after 4 ME-covering turns:", last["ready_to_complete"])
    assert last["ready_to_complete"] is True, (
        "expected completion once ME is deep enough on top of already-covered YOU and US, got False"
    )

print("\nSTEERING FIX VERIFIED — a follow-up conversation opens ME-focused and completion "
      "accounts for coverage already banked from earlier conversations/Discoveries")
