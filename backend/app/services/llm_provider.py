from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import get_settings


@lru_cache
def get_primary_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.primary_llm,
        api_key=settings.openai_api_key,
        temperature=0,
    )


@lru_cache
def get_fallback_llm() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.fallback_llm,
        api_key=settings.anthropic_api_key,
        temperature=0,
    )


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
