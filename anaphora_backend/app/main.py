from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .database import Base, engine, SessionLocal
from .models import Candidate, Discovery
from .discovery_registry import DISCOVERIES
from .routers import conversation_router, blueprint_router, readiness_router, discovery_router, matching_router, preferences_router, profile_router, friends_router

BASE_DIR = Path(__file__).resolve().parent.parent  # anaphora_backend/
TEST_UI_PATH = BASE_DIR / "test_ui" / "index.html"

# Candidate.embedding is a pgvector column, which only compiles against the
# postgresql dialect — local dev defaults to SQLite (zero-setup, see
# config.py), so skip that one table there rather than breaking every
# other feature's local dev experience for a table SQLite can't represent.
if engine.dialect.name == "postgresql":
    Base.metadata.create_all(bind=engine)
else:
    other_tables = [t for t in Base.metadata.sorted_tables if t.name != Candidate.__tablename__]
    Base.metadata.create_all(bind=engine, tables=other_tables)


def sync_discovery_registry() -> None:
    """Idempotently sync code-defined Discoveries into the DB.

    The registry is the source of truth for implemented questionnaires.
    This runs safely on every process start: new Discoveries are inserted,
    and title/status changes are updated without touching user responses.
    """
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
app.include_router(profile_router.router)
app.include_router(friends_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_ui():
    """Dev-only manual test harness for every endpoint. Not part of the product."""
    return FileResponse(TEST_UI_PATH)
