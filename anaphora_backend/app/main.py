from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .database import Base, engine, SessionLocal
from .models import Candidate, Discovery
from .discovery_registry import DISCOVERIES
from .routers import conversation_router, blueprint_router, readiness_router, discovery_router, matching_router, profile_router

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_UI_PATH = BASE_DIR / "test_ui" / "index.html"

if engine.dialect.name == "postgresql":
    Base.metadata.create_all(bind=engine)
else:
    other_tables = [t for t in Base.metadata.sorted_tables if t.name != Candidate.__tablename__]
    Base.metadata.create_all(bind=engine, tables=other_tables)


def sync_discovery_registry() -> None:
    """Idempotently sync code-defined Discoveries into the DB."""
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
app.include_router(profile_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_ui():
    """Dev-only manual test harness for every endpoint. Not part of the product."""
    return FileResponse(TEST_UI_PATH)
