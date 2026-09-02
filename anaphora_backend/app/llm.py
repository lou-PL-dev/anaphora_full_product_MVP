"""Single place that constructs LangChain OpenAI clients.

Every chain used to build its own ChatOpenAI/OpenAIEmbeddings inline,
repeating the same settings.*_api_key wiring at every call site. Centralizing
it here means a future cross-cutting change (timeouts, retries, a shared
client) only needs to happen once.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import settings


def get_chat_llm(model: str | None = None, temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(model=model or settings.openai_model, temperature=temperature, api_key=settings.openai_api_key)


def get_embedder() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
