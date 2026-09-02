"""Regression tests for the four introduction-readiness areas.

Run from anaphora_backend with: pytest test_readiness.py -q
No OpenAI calls or production database are involved.
"""
import os
import uuid
from datetime import date

os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import BlueprintSignal, Discovery, DiscoveryResponse, User
from app.readiness import compute_readiness

TEST_DB_URL = "sqlite:///./test_readiness.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


def _new_db():
    Base.metadata.drop_all(bind=engine)
    tables = [table for table in Base.metadata.sorted_tables if table.name != "candidates"]
    Base.metadata.create_all(bind=engine, tables=tables)
    db = Session()
    db.add(Discovery(id="life_you_are_building", title="What kind of life are you building?", status="active"))
    db.commit()
    return db


def _user(db, *, essentials=False, preferences=False):
    user = User(id=f"u-{uuid.uuid4()}")
    if essentials:
        user.gender = "woman"
        user.birth_date = date(1988, 10, 17)
        user.age = 37
    if preferences:
        user.gender_preference = "men,nonbinary"
        user.preferred_age_range = "30-45"
    db.add(user)
    db.commit()
    return user


def _signal(db, user_id, perspective, category, source="conversation"):
    db.add(BlueprintSignal(
        user_id=user_id,
        perspective=perspective,
        category=category,
        label=f"{perspective}-{category}-{uuid.uuid4()}",
        strength="preference",
        source=source,
    ))
    db.commit()


def _ready_side(db, user_id, perspective):
    categories = {
        "ME": ["personality", "lifestyle", "relationship_behavior"],
        "IDEAL_PARTNER": ["personality", "lifestyle", "physical_type"],
        "US": ["relationship_shape", "connection_affection", "shared_direction"],
    }[perspective]
    for category in categories:
        _signal(db, user_id, perspective, category)


def _discovery(db, user_id):
    db.add(DiscoveryResponse(
        user_id=user_id,
        discovery_id="life_you_are_building",
        question_id="q1",
        response="answer",
    ))
    db.commit()


def test_new_user_is_zero():
    db = _new_db()
    user = _user(db)
    assert compute_readiness(db, user.id)[0] == 0
    db.close()


def test_discovery_only_is_twenty():
    db = _new_db()
    user = _user(db)
    _discovery(db, user.id)
    assert compute_readiness(db, user.id)[0] == 20
    db.close()


def test_your_essentials_only_are_ten_and_parent_not_met():
    db = _new_db()
    user = _user(db, essentials=True)
    score, breakdown = compute_readiness(db, user.id)
    assert score == 10
    intro = breakdown["introduction_essentials"]
    assert intro["earned"] == 10
    assert intro["met"] is False
    assert intro["parts"]["your_essentials"]["met"] is True
    assert intro["parts"]["meeting_preferences"]["met"] is False
    db.close()


def test_meeting_preferences_only_are_ten_and_parent_not_met():
    db = _new_db()
    user = _user(db, preferences=True)
    score, breakdown = compute_readiness(db, user.id)
    assert score == 10
    assert breakdown["introduction_essentials"]["met"] is False
    db.close()


def test_both_introduction_essentials_are_twenty_and_met():
    db = _new_db()
    user = _user(db, essentials=True, preferences=True)
    score, breakdown = compute_readiness(db, user.id)
    assert score == 20
    assert breakdown["introduction_essentials"]["earned"] == 20
    assert breakdown["introduction_essentials"]["met"] is True
    db.close()


def test_age_without_birth_date_does_not_unlock_your_essentials():
    db = _new_db()
    user = User(id=f"u-{uuid.uuid4()}", gender="woman", age=37)
    db.add(user)
    db.commit()
    assert compute_readiness(db, user.id)[0] == 0
    db.close()


def test_one_me_signal_plus_discovery_does_not_unlock_me_gate():
    db = _new_db()
    user = _user(db)
    _discovery(db, user.id)
    _signal(db, user.id, "ME", "lifestyle", source="discovery")
    assert compute_readiness(db, user.id)[0] == 20
    db.close()


def test_sufficient_me_profile_is_twenty():
    db = _new_db()
    user = _user(db)
    _ready_side(db, user.id, "ME")
    assert compute_readiness(db, user.id)[0] == 20
    db.close()


def test_sufficient_ideal_partner_profile_is_twenty():
    db = _new_db()
    user = _user(db)
    _ready_side(db, user.id, "IDEAL_PARTNER")
    assert compute_readiness(db, user.id)[0] == 20
    db.close()


def test_missing_mandatory_category_does_not_unlock_profile_gate():
    db = _new_db()
    user = _user(db)
    for category in ["personality", "lifestyle", "physical_type"]:
        _signal(db, user.id, "ME", category)
    assert compute_readiness(db, user.id)[0] == 0
    db.close()


def test_all_four_areas_reach_one_hundred():
    db = _new_db()
    user = _user(db, essentials=True, preferences=True)
    _discovery(db, user.id)
    _ready_side(db, user.id, "ME")
    _ready_side(db, user.id, "IDEAL_PARTNER")
    _ready_side(db, user.id, "US")
    score, breakdown = compute_readiness(db, user.id)
    assert score == 100
    assert all(item["met"] for item in breakdown.values())
    db.close()


def test_extra_discovery_responses_do_not_add_more_points():
    db = _new_db()
    user = _user(db)
    _discovery(db, user.id)
    db.add(DiscoveryResponse(
        user_id=user.id,
        discovery_id="life_you_are_building",
        question_id="q2",
        response="another answer",
    ))
    db.commit()
    assert compute_readiness(db, user.id)[0] == 20
    db.close()
