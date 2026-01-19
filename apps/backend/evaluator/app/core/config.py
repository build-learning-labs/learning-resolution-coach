"""Evaluator configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Evaluator service settings."""
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    EVALUATOR_PORT: int = 8003
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    
    # Code sandbox (for future implementation)
    SANDBOX_ENABLED: bool = False
    SANDBOX_TIMEOUT_SECONDS: int = 10
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
