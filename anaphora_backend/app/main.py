from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .database import Base, engine
from .models import Candidate
from .routers import conversation_router, blueprint_router, readiness_router, discovery_router, matching_router

BASE_DIR = Path(__file__).resolve().parent.parent  # anaphora_backend/
TEST_UI_PATH = BASE_DIR / "test_ui" / "index.html"

# Candidate.embedding is a pgvector column, which only compiles against the
# postgresql dialect — local dev defaults to SQLite (zero-setup, see
# config.py), so skip that one table there rather than breaking every
# other feature's local dev experience for a table SQLite can't represent
# anyway. The deployed instance (Render Postgres, with `CREATE EXTENSION
# vector` run once — see anaphora_backend/README.md) creates it normally.
if engine.dialect.name == "postgresql":
    Base.metadata.create_all(bind=engine)
else:
    other_tables = [t for t in Base.metadata.sorted_tables if t.name != Candidate.__tablename__]
    Base.metadata.create_all(bind=engine, tables=other_tables)

app = FastAPI(title="Anaphora MVP API")

# Wide-open CORS for the MVP so a Claude Design frontend (any localhost
# port, or a preview URL) can call this without extra config. Tighten this
# to your actual frontend origin(s) before anything resembling production.
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_ui():
    """Dev-only manual test harness for every endpoint. Not part of the
    product — see test_ui/index.html."""
    return FileResponse(TEST_UI_PATH)