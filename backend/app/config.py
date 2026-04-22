from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: str = "development"
    log_level: str = "INFO"

    # LLM providers
    openai_api_key: str
    anthropic_api_key: str = ""

    # Supabase
    supabase_url: str
    supabase_service_role_key: str

    # App
    cors_origins: list[str] = ["http://localhost:8501"]

    # Model names
    primary_llm: str = "gpt-4o"
    fallback_llm: str = "claude-sonnet-4-5"
    embedding_model: str = "text-embedding-3-small"

    # RAG
    rag_top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
