"""
Central settings, loaded once from .env.
"""
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent          # anaphora_backend/
REPO_ROOT = BASE_DIR.parent                                  # repo root — shared .env lives here


class Settings(BaseSettings):
    # Defaults to a local SQLite file so the app runs with zero setup.
    # For real use, point this at your Supabase Postgres connection string,
    # e.g. postgresql://postgres:[password]@[host]:5432/postgres
    database_url: str = f"sqlite:///{BASE_DIR / 'anaphora.db'}"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    class Config:
        env_file = REPO_ROOT / ".env"
        extra = "ignore"  # the shared .env has keys for other labs/projects
                          # (hf_token, tavily_api_key, etc.) — only read what
                          # this Settings class actually declares above


settings = Settings()