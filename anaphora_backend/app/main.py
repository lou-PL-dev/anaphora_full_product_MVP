from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text

from .database import Base, engine, SessionLocal
from .models import Candidate, Discovery
from .discovery_registry import DISCOVERIES
from .routers import conversation_router, blueprint_router, readiness_router, discovery_router, matching_router, preferences_router, friends_router, admin_router

BASE_DIR = Path(__file__).resolve().parent.parent  # anaphora_backend/
TEST_UI_PATH = BASE_DIR / "test_ui" / "index.html"

if engine.dialect.name == "postgresql":
    Base.metadata.create_all(bind=engine)
else:
    other_tables = [t for t in Base.metadata.sorted_tables if t.name != Candidate.__tablename__]
    Base.metadata.create_all(bind=engine, tables=other_tables)


def sync_schema() -> None:
    """Small idempotent MVP schema sync for additive columns."""
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_date DATE"))
            conn.execute(text("ALTER TABLE blueprint_signals ADD COLUMN IF NOT EXISTS evidence_ids JSON"))
        else:
            columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
            if "birth_date" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN birth_date DATE"))
            signal_columns = {
                row[1] for row in conn.execute(text("PRAGMA table_info(blueprint_signals)"))
            }
            if "evidence_ids" not in signal_columns:
                conn.execute(text("ALTER TABLE blueprint_signals ADD COLUMN evidence_ids JSON"))


sync_schema()


def sync_indexes() -> None:
    """Create indexes the model definitions declare on FK/lookup columns
    that get filtered on nearly every request.

    create_all() above only creates missing *tables* — it never alters a
    table that already exists, so a column gaining index=True has no effect
    on the live production DB. CREATE INDEX IF NOT EXISTS is idempotent and
    safe to run on every boot, same spirit as sync_discovery_registry below.
    """
    statements = [
        "CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON conversations (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_blueprint_signals_user_id ON blueprint_signals (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_blueprint_evidence_user_id ON blueprint_evidence (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_discovery_responses_user_id ON discovery_responses (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_discovery_responses_discovery_id ON discovery_responses (discovery_id)",
        "CREATE INDEX IF NOT EXISTS ix_friend_invites_user_id ON friend_invites (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_friend_responses_invite_id ON friend_responses (invite_id)",
        "CREATE INDEX IF NOT EXISTS ix_friend_signals_response_id ON friend_signals (response_id)",
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


sync_indexes()


def migrate_blueprint_taxonomy() -> None:
    """Idempotently move existing user signals into ME / YOU / US.

    Candidate JSON is intentionally not rewritten here; the candidate
    regeneration command rebuilds it with the new taxonomy and embeddings.
    """
    mappings = [
        ("ME", "relationship_dynamic", "ME", "relationship_behavior"),
        ("ME", "love_language", "ME", "relationship_behavior"),
        ("ME", "values", "ME", "core_values"),
        ("ME", "dealbreakers", "US", "boundaries"),
        ("ME", "physical_type", "IDEAL_PARTNER", "physical_type"),
        ("IDEAL_PARTNER", "relationship_dynamic", "US", "relationship_shape"),
        ("IDEAL_PARTNER", "love_language", "US", "connection_affection"),
        ("IDEAL_PARTNER", "values", "US", "shared_direction"),
        ("IDEAL_PARTNER", "dealbreakers", "US", "boundaries"),
    ]
    with engine.begin() as conn:
        for old_perspective, old_category, new_perspective, new_category in mappings:
            conn.execute(text(
                "UPDATE blueprint_signals SET perspective = :new_p, category = :new_c "
                "WHERE perspective = :old_p AND category = :old_c"
            ), {"new_p": new_perspective, "new_c": new_category,
                "old_p": old_perspective, "old_c": old_category})


migrate_blueprint_taxonomy()


def sync_discovery_registry() -> None:
    db = SessionLocal()
    try:
        for spec in DISCOVERIES.values():
            row = db.get(Discovery, spec.id)
            if row is None:
                db.add(Discovery(id=spec.id, title=spec.title, status=spec.status))
            else:
                row.title = spec.title
                row.status = spec.status
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


sync_discovery_registry()

app = FastAPI(title="Anaphora MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversation_router.router)
app.include_router(blueprint_router.router)
app.include_router(readiness_router.router)
app.include_router(discovery_router.router)
app.include_router(matching_router.router)
app.include_router(preferences_router.router)
app.include_router(friends_router.router)
app.include_router(admin_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_ui():
    """Dev-only manual test harness for every endpoint. Not part of the product."""
    return FileResponse(TEST_UI_PATH)
