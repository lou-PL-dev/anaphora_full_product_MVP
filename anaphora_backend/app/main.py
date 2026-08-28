from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .database import Base, engine
from .routers import conversation_router, blueprint_router, readiness_router, discovery_router

BASE_DIR = Path(__file__).resolve().parent.parent  # anaphora_backend/
TEST_UI_PATH = BASE_DIR / "test_ui" / "index.html"

Base.metadata.create_all(bind=engine)

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_ui():
    """Dev-only manual test harness for every endpoint. Not part of the
    product — see test_ui/index.html."""
    return FileResponse(TEST_UI_PATH)