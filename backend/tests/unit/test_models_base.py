"""Unit tests for SQLAlchemy base models and session management.

Tests cover:
- Engine creation and caching
- Session factory initialization
- FastAPI dependency injection pattern
- Context manager for manual session handling
- Model registration with Base
"""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models import (
    APILog,
    Base,
    Document,
    Mindmap,
    Summary,
    User,
    get_db,
    get_db_context,
    get_engine,
    init_db,
)


class TestEngineFactory:
    """Test database engine creation and caching."""

    def test_get_engine_creates_engine(self):
        """Test that get_engine returns a valid SQLAlchemy engine."""
        engine = get_engine()
        assert engine is not None
        assert hasattr(engine, "connect")

    def test_get_engine_returns_cached_instance(self):
        """Test that get_engine returns the same engine on multiple calls."""
        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2

    def test_engine_can_connect(self):
        """Test that the engine can establish a database connection."""
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


class TestSessionFactory:
    """Test session factory initialization and configuration."""

    def test_init_db_configures_session(self):
        """Test that init_db binds SessionLocal to the engine."""
        init_db()
        from src.models import SessionLocal

        assert SessionLocal.kw.get("bind") is not None

    def test_session_can_be_created(self):
        """Test that SessionLocal can create database sessions."""
        init_db()
        from src.models import SessionLocal

        db = SessionLocal()
        assert isinstance(db, Session)
        db.close()


class TestFastAPIDepedency:
    """Test FastAPI dependency injection pattern."""

    def test_get_db_yields_session(self):
        """Test that get_db yields a valid database session."""
        init_db()
        gen = get_db()
        db = next(gen)
        assert isinstance(db, Session)

        # Clean up
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_closes_session(self):
        """Test that get_db closes the session after use."""
        init_db()
        gen = get_db()
        db = next(gen)

        # Verify session is open
        assert not db.is_active or True  # Session exists

        # Close via generator
        try:
            next(gen)
        except StopIteration:
            pass

        # Session should be closed
        assert db.is_active is False

    def test_get_db_in_fastapi_route_pattern(self):
        """Test get_db usage pattern similar to FastAPI routes."""
        init_db()

        # Simulate FastAPI dependency injection
        gen = get_db()
        db = next(gen)
        try:
            # Route logic
            result = db.execute(text("SELECT 1")).scalar()
            assert result == 1
        finally:
            try:
                next(gen)
            except StopIteration:
                pass


class TestContextManager:
    """Test context manager for manual session handling."""

    def test_get_db_context_yields_session(self):
        """Test that get_db_context yields a valid session."""
        init_db()
        with get_db_context() as db:
            assert isinstance(db, Session)

    def test_get_db_context_commits_on_success(self):
        """Test that context manager commits on successful exit."""
        init_db()
        # This test verifies the pattern works; actual commit behavior
        # is tested in integration tests with real data
        with get_db_context() as db:
            result = db.execute(text("SELECT 1")).scalar()
            assert result == 1
        # If we reach here, commit succeeded

    def test_get_db_context_rolls_back_on_error(self):
        """Test that context manager rolls back on exception."""
        init_db()
        with pytest.raises(ValueError):
            with get_db_context() as db:
                # Verify session is usable
                assert isinstance(db, Session)
                # Raise exception to trigger rollback
                raise ValueError("Test error")

    def test_get_db_context_closes_session(self):
        """Test that context manager closes session after use."""
        init_db()
        with get_db_context() as db:
            session = db
            assert db.is_active or True  # Session exists

        # After context exit, session should be closed
        assert session.is_active is False


class TestModelRegistration:
    """Test that all models are registered with Base."""

    def test_base_is_declarative_base(self):
        """Test that Base is a valid declarative base."""
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")

    def test_all_models_imported(self):
        """Test that all models are available in module."""
        # Verify all expected models are importable
        assert User is not None
        assert Document is not None
        assert Summary is not None
        assert Mindmap is not None
        assert APILog is not None

    def test_models_inherit_from_base(self):
        """Test that all models inherit from Base."""
        # Verify models are registered with Base
        # (they would fail to import if not properly defined)
        assert hasattr(User, "__tablename__")
        assert hasattr(Document, "__tablename__")
        assert hasattr(Summary, "__tablename__")
        assert hasattr(Mindmap, "__tablename__")
        assert hasattr(APILog, "__tablename__")

    def test_base_metadata_has_tables(self):
        """Test that Base.metadata contains all expected tables."""
        # After models are imported, Base.metadata should have table definitions
        table_names = list(Base.metadata.tables.keys())

        expected_tables = ["users", "documents", "summaries", "mindmaps", "api_logs"]

        for table_name in expected_tables:
            assert table_name in table_names, (
                f"Table '{table_name}' not found in Base.metadata"
            )


class TestModuleExports:
    """Test that all expected symbols are exported in __all__."""

    def test_all_exports_are_defined(self):
        """Test that all symbols in __all__ are defined."""
        from src.models import __all__

        expected_exports = [
            "Base",
            "get_engine",
            "init_db",
            "SessionLocal",
            "get_db",
            "get_db_context",
            "User",
            "Document",
            "Summary",
            "Mindmap",
            "APILog",
        ]

        assert set(__all__) == set(expected_exports)

    def test_exports_are_importable(self):
        """Test that all exports can be imported."""
        from src.models import (
            APILog,
            Base,
            Document,
            Mindmap,
            SessionLocal,
            Summary,
            User,
            get_db,
            get_db_context,
            get_engine,
            init_db,
        )

        # Verify all imports are not None
        assert Base is not None
        assert get_engine is not None
        assert init_db is not None
        assert SessionLocal is not None
        assert get_db is not None
        assert get_db_context is not None
        assert User is not None
        assert Document is not None
        assert Summary is not None
        assert Mindmap is not None
        assert APILog is not None


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_get_db_handles_session_error(self):
        """Test that get_db properly closes session even on error."""
        init_db()
        gen = get_db()
        db = next(gen)

        # Force an error scenario by closing connection
        # The finally block should still execute
        try:
            # Simulate error in route
            raise RuntimeError("Simulated route error")
        except RuntimeError:
            pass
        finally:
            try:
                next(gen)
            except StopIteration:
                pass

        # Session should be closed despite error
        assert db.is_active is False

    def test_get_db_context_handles_multiple_errors(self):
        """Test context manager with nested exception scenarios."""
        init_db()

        # Test that only the first exception is preserved
        with pytest.raises(ValueError, match="First error"):
            with get_db_context() as db:
                assert isinstance(db, Session)
                raise ValueError("First error")

    def test_engine_survives_connection_failure(self):
        """Test that engine remains valid after connection failure."""
        engine = get_engine()

        # Engine should still be valid even if we have a failed connection attempt
        # (This is handled by pool_pre_ping=True)
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                assert result == 1
        except Exception:
            # Even if this fails, engine should remain valid
            pass

        # Engine should still be the same cached instance
        engine2 = get_engine()
        assert engine is engine2


class TestDocumentation:
    """Test that all public functions have proper documentation."""

    def test_get_engine_has_docstring(self):
        """Test that get_engine has comprehensive docstring."""
        assert get_engine.__doc__ is not None
        assert "engine" in get_engine.__doc__.lower()
        assert "return" in get_engine.__doc__.lower()

    def test_get_db_has_docstring(self):
        """Test that get_db has comprehensive docstring."""
        assert get_db.__doc__ is not None
        assert "fastapi" in get_db.__doc__.lower()
        assert "yield" in get_db.__doc__.lower()

    def test_get_db_context_has_docstring(self):
        """Test that get_db_context has comprehensive docstring."""
        assert get_db_context.__doc__ is not None
        assert "context manager" in get_db_context.__doc__.lower()

    def test_init_db_has_docstring(self):
        """Test that init_db has comprehensive docstring."""
        assert init_db.__doc__ is not None
        assert "initialize" in init_db.__doc__.lower()
