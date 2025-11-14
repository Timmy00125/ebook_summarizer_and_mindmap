"""SQLAlchemy base models and database session management.

This module provides:
- Declarative Base class for all ORM models
- Database engine factory with connection pooling
- Session management utilities for FastAPI dependency injection
- Context managers for manual session handling

All models inherit from Base and are registered for Alembic migrations.
"""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..config import get_settings

# ============================================================================
# DECLARATIVE BASE
# ============================================================================

# Create the declarative base for all models to inherit from
Base = declarative_base()


# ============================================================================
# DATABASE ENGINE FACTORY
# ============================================================================

# Global engine instance (initialized on first call to get_engine)
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Get or create the database engine with connection pooling.

    The engine is created once and cached for the lifetime of the application.
    Connection pool settings are loaded from configuration.

    Returns:
        Engine: SQLAlchemy engine instance with configured connection pool

    Example:
        >>> engine = get_engine()
        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("SELECT 1"))
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        _engine = create_engine(
            str(settings.database_url),
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_pool_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.db_echo,  # SQL logging for debugging
        )

    return _engine


# ============================================================================
# SESSION FACTORY
# ============================================================================

# Session factory for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=None,  # Will be bound when engine is available
)


def init_db() -> None:
    """Initialize database by binding SessionLocal to engine.

    This should be called once during application startup to configure
    the session factory with the database engine.

    Example:
        >>> # In main.py startup event
        >>> init_db()
    """
    engine = get_engine()
    SessionLocal.configure(bind=engine)


# ============================================================================
# FASTAPI DEPENDENCY INJECTION
# ============================================================================


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session.

    Yields a SQLAlchemy session that is automatically closed after use.
    Use this as a dependency in FastAPI route functions.

    Yields:
        Session: SQLAlchemy database session

    Example:
        >>> from fastapi import Depends
        >>> from sqlalchemy.orm import Session
        >>>
        >>> @app.get("/users/{user_id}")
        >>> async def get_user(
        ...     user_id: int,
        ...     db: Session = Depends(get_db)
        ... ):
        ...     return db.query(User).filter(User.id == user_id).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# CONTEXT MANAGER FOR MANUAL SESSION HANDLING
# ============================================================================


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions outside of FastAPI routes.

    Use this for background tasks, scripts, or any non-route database access.
    The session is automatically committed on success or rolled back on error.

    Yields:
        Session: SQLAlchemy database session

    Example:
        >>> from models import get_db_context, User
        >>>
        >>> with get_db_context() as db:
        ...     user = User(email="test@example.com", name="Test User")
        ...     db.add(user)
        ...     # Automatically commits on exit
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# MODEL IMPORTS
# ============================================================================

# Import all models to ensure they're registered with Base
# This is REQUIRED for Alembic to detect models for auto-migration generation
from .api_log import APILog  # noqa: E402
from .document import Document  # noqa: E402
from .mindmap import Mindmap  # noqa: E402
from .summary import Summary  # noqa: E402
from .user import User  # noqa: E402

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Declarative base
    "Base",
    # Engine management
    "get_engine",
    "init_db",
    # Session management
    "SessionLocal",
    "get_db",
    "get_db_context",
    # Models
    "User",
    "Document",
    "Summary",
    "Mindmap",
    "APILog",
]
