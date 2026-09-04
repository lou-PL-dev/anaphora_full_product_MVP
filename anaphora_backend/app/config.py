"""
Central settings, loaded once from .env.
"""
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent          # anaphora_backend/
REPO_ROOT = BASE_DIR.parent                                  # repo root — shared .env lives here

# Pydantic's own env_file loading below only populates the fields Settings
# declares — it never writes the .env file's other keys into the real process
# environment. LangChain tracing is auto-instrumented from os.environ, so load
# the shared file explicitly. Real deployment env vars still win.
load_dotenv(REPO_ROOT / ".env", override=False)


class Settings(BaseSettings):
    # Defaults to a local SQLite file so the app runs with zero setup.
    database_url: str = f"sqlite:///{BASE_DIR / 'anaphora.db'}"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_conversation_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    # Explicitly opt-in safeguard for a synthetic golden candidate used in
    # live demos. Normal matching is unchanged unless this is true, and even
    # then only a fixture targeted to the current user may use the fallback.
    anaphora_demo_mode: bool = False

    # Small private tester dashboard only. Set ADMIN_SECRET in Render; the
    # secret is never bundled into the frontend and is entered manually on
    # /admin/test-sessions.
    admin_secret: str = ""

    class Config:
        env_file = REPO_ROOT / ".env"
        extra = "ignore"


settings = Settings()
