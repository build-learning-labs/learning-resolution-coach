"""Core Agent configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Core Agent service settings."""
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    CORE_AGENT_PORT: int = 8001
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""
    
    # Other services
    RAG_WORKER_URL: str = "http://localhost:8002"
    EVALUATOR_URL: str = "http://localhost:8003"
    
    # Opik
    OPIK_API_KEY: str = ""
    OPIK_PROJECT: str = "learning-resolution-coach"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
