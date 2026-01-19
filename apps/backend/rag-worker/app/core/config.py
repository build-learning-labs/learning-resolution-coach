"""RAG Worker configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """RAG Worker settings."""
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    RAG_WORKER_PORT: int = 8002
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    # Vector Store
    VECTOR_STORE: str = "chromadb"
    CHROMA_PERSIST_DIR: str = "./chromadb_data"
    CHROMA_COLLECTION: str = "learning_resources"
    
    # Pinecone (optional)
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_INDEX: str = ""
    
    # LLM for embeddings
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
