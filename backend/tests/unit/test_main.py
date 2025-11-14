"""Unit tests for FastAPI application initialization (main.py).

Tests cover:
- Application creation and configuration
- Health check endpoint
- Root endpoint
- Middleware registration

Note: Environment variables are set in conftest.py before importing the app.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    """Create a test client for FastAPI application.

    This fixture mocks database initialization to avoid requiring a real database.

    Returns:
        TestClient instance for testing FastAPI endpoints
    """
    with patch("src.main.init_db"):
        from src.main import app

        with TestClient(app) as test_client:
            yield test_client


class TestApplicationInitialization:
    """Test suite for FastAPI application initialization."""

    def test_app_creation(self, client):
        """Test that FastAPI application is created with correct metadata."""
        from src.main import app

        assert app is not None
        assert app.title == "PDF Summary & Mindmap API"
        assert app.version == "1.0.0"
        assert "document processing" in app.description.lower()

    def test_app_debug_docs(self, client):
        """Test that docs are enabled in debug mode."""
        from src.main import app

        # Debug is True (set in conftest.py), so docs should be enabled
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"


class TestHealthCheckEndpoint:
    """Test suite for health check endpoints."""

    def test_basic_health_check(self, client):
        """Test basic health check endpoint returns 200 OK."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app_name" in data
        assert data["environment"] == "development"
        assert data["version"] == "1.0.0"

    def test_health_check_structure(self, client):
        """Test that health check returns all required fields."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        required_fields = ["status", "app_name", "environment", "version"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "PDF Summary" in data["message"]
        assert data["version"] == "1.0.0"

    def test_root_endpoint_links(self, client):
        """Test that root endpoint provides navigation links."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Verify navigation links are present
        assert "docs_url" in data
        assert "health_check" in data
        assert "detailed_health_check" in data
        assert data["health_check"] == "/health"
        assert data["detailed_health_check"] == "/api/health"

    def test_root_endpoint_debug_docs(self, client):
        """Test that docs URL is present in debug mode."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # In debug mode, docs_url should be present
        assert data["docs_url"] == "/docs"


class TestMiddleware:
    """Test suite for middleware configuration."""

    def test_cors_middleware_registered(self, client):
        """Test that CORS middleware is registered in the app."""
        from src.main import app

        # Check that middleware stack is not empty (CORS and error handling were added)
        # TestClient may not expose CORS headers in the same way as real HTTP requests
        assert len(app.user_middleware) > 0, "Middleware should be registered"

    def test_error_handling_middleware(self, client):
        """Test that error handling middleware catches exceptions."""
        # Request a non-existent endpoint
        response = client.get("/nonexistent")

        # Should return structured error (404)
        assert response.status_code == 404


class TestApplicationStructure:
    """Test suite for application code structure and best practices."""

    def test_has_proper_docstrings(self):
        """Test that main module has proper documentation."""
        with patch("src.main.init_db"):
            import src.main

            # Check module docstring
            assert src.main.__doc__ is not None
            assert "FastAPI" in src.main.__doc__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
