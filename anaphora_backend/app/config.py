"""
Central settings, loaded once from .env.
"""
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent          # anaphora_backend/
REPO_ROOT = BASE_DIR.parent                                  # repo root — shared .env lives here

# Pydantic's own env_file loading below only populates the fields Settings
# declares (database_url/openai_api_key/openai_model) — it never writes the
# .env file's other keys into the real process environment. LangChain's
# tracing (LANGCHAIN_TRACING_V2/LANGCHAIN_API_KEY/LANGCHAIN_PROJECT) is
# auto-instrumented purely by reading os.environ, so without this explicit
# load those vars stay invisible to it even when they're right there in
# .env. override=False so real env vars (e.g. set in Render's dashboard for
# the deployed backend) always win over anything in a local .env file.
load_dotenv(REPO_ROOT / ".env", override=False)


class Settings(BaseSettings):
    # Defaults to a local SQLite file so the app runs with zero setup.
    # For real use, point this at your Supabase Postgres connection string,
    # e.g. postgresql://postgres:[password]@[host]:5432/postgres
    database_url: str = f"sqlite:///{BASE_DIR / 'anaphora.db'}"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    # The conversation chain alone gets a stronger model: it has to hold an
    # entire transcript's category-coverage state in mind while improvising
    # natural, non-repetitive phrasing every turn — extraction and
    # discovery insight synthesis are simpler one-shot structured-output
    # tasks that gpt-4o-mini handles fine, so only this one call site's
    # cost goes up.
    openai_conversation_model: str = "gpt-4o"

    class Config:
        env_file = REPO_ROOT / ".env"
        extra = "ignore"  # the shared .env has keys for other labs/projects
                          # (hf_token, tavily_api_key, etc.) — only read what
                          # this Settings class actually declares above


settings = Settings()