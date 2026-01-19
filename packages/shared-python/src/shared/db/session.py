"""Database session and engine configuration."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from functools import lru_cache


class DatabaseConfig:
    """Database configuration supporting multiple dialects.
    
    Supports:
    - SQLite (development)
    - PostgreSQL (production)
    - PostgreSQL with asyncpg (async production)
    """

    SUPPORTED_DIALECTS = ["sqlite", "postgresql", "postgresql+asyncpg"]

    @classmethod
    def get_engine(cls, database_url: str):
        """Create SQLAlchemy engine with appropriate settings per dialect."""
        dialect = database_url.split(":")[0]
        
        if dialect not in cls.SUPPORTED_DIALECTS:
            raise ValueError(
                f"Unsupported database dialect: {dialect}. "
                f"Supported: {cls.SUPPORTED_DIALECTS}"
            )

        connect_args = {}
        pool_settings = {}

        if dialect == "sqlite":
            # SQLite-specific settings
            connect_args["check_same_thread"] = False
        else:
            # PostgreSQL connection pool settings
            pool_settings = {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 1800,
            }

        return create_engine(
            database_url,
            connect_args=connect_args,
            echo=False,
            **pool_settings,
        )


# Global engine and session factory (lazy initialization)
_engine = None
_SessionLocal = None


def get_engine(database_url: str | None = None):
    """Get or create the database engine."""
    global _engine
    
    if _engine is None:
        if database_url is None:
            import os
            database_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
        _engine = DatabaseConfig.get_engine(database_url)
    
    return _engine


def get_session_factory(database_url: str | None = None) -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine(database_url)
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    
    return _SessionLocal


def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    """Dependency for getting database sessions.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_session)):
            ...
    """
    SessionLocal = get_session_factory(database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(database_url: str | None = None):
    """Initialize database tables.
    
    Use Alembic migrations for production. This is for development only.
    """
    from shared.db.base import Base
    
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
