from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import blueprint_canonicalizer as canonicalizer
from app.database import Base
from app.models import BlueprintEvidence, BlueprintSignal, User
from app.schemas import CanonicalBlueprintResult


def _evidence(evidence_id, perspective, category, label, strength="preference"):
    return BlueprintEvidence(
        id=evidence_id,
        user_id="u1",
        perspective=perspective,
        category=category,
        label=label,
        strength=strength,
        source="conversation:test",
        evidence_text=label,
        confidence=0.9,
        explicit=True,
    )


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine, tables=[
        User.__table__, BlueprintSignal.__table__, BlueprintEvidence.__table__,
    ])
    return sessionmaker(bind=engine)()


def test_materialize_merges_splits_and_reclassifies_reported_clusters():
    evidence = [
        _evidence("warm", "IDEAL_PARTNER", "personality", "Warm"),
        _evidence("smart", "IDEAL_PARTNER", "personality", "Smart"),
        _evidence("warm-smart", "IDEAL_PARTNER", "personality", "Warm and smart", "strong_preference"),
        _evidence("read-1", "ME", "lifestyle", "Likes to read"),
        _evidence("read-2", "ME", "lifestyle", "Enjoys reading"),
        _evidence("conflict-1", "ME", "relationship_behavior", "Needs time to process conflicts"),
        _evidence("conflict-2", "ME", "relationship_behavior", "Processes before discussing conflicts"),
        _evidence("values-1", "ME", "core_values", "Values honesty, transparency, and courage"),
        _evidence("values-2", "ME", "core_values", "Honesty, transparency, courage"),
        _evidence("kind-adventure", "IDEAL_PARTNER", "lifestyle", "Kind and adventurous"),
    ]
    result = CanonicalBlueprintResult.model_validate({
        "signals": [
            {"perspective": "IDEAL_PARTNER", "category": "personality", "label": "Warm", "evidence_ids": ["warm", "warm-smart"]},
            {"perspective": "IDEAL_PARTNER", "category": "personality", "label": "Smart", "evidence_ids": ["smart", "warm-smart"]},
            {"perspective": "ME", "category": "lifestyle", "label": "Enjoys reading", "evidence_ids": ["read-2", "read-1"]},
            {"perspective": "ME", "category": "relationship_behavior", "label": "Takes time to process before discussing conflict", "evidence_ids": ["conflict-1", "conflict-2"]},
            {"perspective": "ME", "category": "core_values", "label": "Honesty, transparency, and courage", "evidence_ids": ["values-1", "values-2"]},
            {"perspective": "IDEAL_PARTNER", "category": "personality", "label": "Kind", "evidence_ids": ["kind-adventure"]},
            {"perspective": "IDEAL_PARTNER", "category": "personality", "label": "Adventurous", "evidence_ids": ["kind-adventure"]},
        ],
        "narrative": "You hope to meet someone warm, smart, kind, and adventurous.",
    })

    projection = canonicalizer._materialize(result, evidence)

    assert len(projection) == 7
    assert next(row for row in projection if row["label"] == "Warm")["strength"] == "strong_preference"
    assert sum(row["label"] == "Enjoys reading" for row in projection) == 1
    assert sum("process" in row["label"].casefold() for row in projection) == 1
    assert all(
        row["category"] == "personality"
        for row in projection
        if row["label"] in {"Kind", "Adventurous"}
    )


def test_user_correction_controls_strength_without_upgrading_other_evidence():
    original = _evidence("original", "IDEAL_PARTNER", "personality", "Warm", "hard_requirement")
    correction = _evidence("correction", "IDEAL_PARTNER", "personality", "Warm", "preference")
    correction.source = "user_correction:signal-1"
    correction.supersedes_evidence_ids = ["original"]
    result = CanonicalBlueprintResult.model_validate({
        "signals": [{
            "perspective": "IDEAL_PARTNER",
            "category": "personality",
            "label": "Warm",
            "evidence_ids": ["correction", "original"],
        }],
        "narrative": "You are drawn to someone warm.",
    })

    projection = canonicalizer._materialize(result, [original, correction])

    assert projection[0]["strength"] == "preference"


def test_backfill_is_once_and_rebuild_replaces_appended_narrative(monkeypatch):
    db = _session()
    user = User(id="u1", blueprint_narrative="Old paragraph.\n\nRepeated paragraph.")
    old = BlueprintSignal(
        id="old-signal",
        user_id="u1",
        perspective="ME",
        category="lifestyle",
        label="Likes to read",
        strength="preference",
        source="conversation:old",
    )
    db.add_all([user, old])
    db.commit()

    assert canonicalizer.ensure_evidence_backfill(db, "u1") == 1
    assert canonicalizer.ensure_evidence_backfill(db, "u1") == 0

    monkeypatch.setattr(canonicalizer, "canonicalize_evidence", lambda rows: CanonicalBlueprintResult.model_validate({
        "signals": [{
            "perspective": "ME",
            "category": "lifestyle",
            "label": "Enjoys reading",
            "evidence_ids": [rows[0].id],
        }],
        "narrative": "",
    }))
    canonicalizer.rebuild_blueprint(db, user)
    db.commit()

    rebuilt = db.query(BlueprintSignal).filter_by(user_id="u1").all()
    assert [row.label for row in rebuilt] == ["Enjoys reading"]
    assert rebuilt[0].source == "canonical"
    assert user.blueprint_narrative is None
    assert db.query(BlueprintEvidence).filter_by(user_id="u1").count() == 1


def test_invalid_rebuild_does_not_delete_existing_projection(monkeypatch):
    db = _session()
    user = User(id="u1", blueprint_narrative="Existing portrait")
    old = BlueprintSignal(
        id="old-signal",
        user_id="u1",
        perspective="ME",
        category="lifestyle",
        label="Enjoys reading",
        strength="preference",
        source="canonical",
    )
    raw = _evidence("raw", "ME", "lifestyle", "Enjoys reading")
    db.add_all([user, old, raw])
    db.commit()

    monkeypatch.setattr(canonicalizer, "canonicalize_evidence", lambda rows: CanonicalBlueprintResult.model_validate({
        "signals": [{
            "perspective": "ME",
            "category": "lifestyle",
            "label": "Invented",
            "evidence_ids": ["not-real"],
        }],
        "narrative": "",
    }))

    try:
        canonicalizer.rebuild_blueprint(db, user)
        assert False, "Expected invalid provenance to fail"
    except ValueError:
        pass

    assert db.query(BlueprintSignal).filter_by(user_id="u1").one().label == "Enjoys reading"
