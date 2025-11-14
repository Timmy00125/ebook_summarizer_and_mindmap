"""Unit tests for health check endpoint.

Tests cover:
- Health check with all services healthy
- Health check with database errors
- Health check with Gemini API errors
- Response schema validation
- Timestamp format validation
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.api.routes.health import check_database, check_gemini_api
from src.main import app

# Create test client
client = TestClient(app)


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestCheckDatabase:
    """Test database connectivity check."""

    @patch("src.api.routes.health.get_engine")
    def test_database_ok(self, mock_get_engine):
        """Test database check returns 'ok' when database is accessible."""
        # Mock successful database connection
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_result.fetchone.return_value = (1,)

        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        result = check_database()

        assert result == "ok"
        mock_conn.execute.assert_called_once()

    @patch("src.api.routes.health.get_engine")
    def test_database_error_connection_failed(self, mock_get_engine):
        """Test database check returns 'error' when connection fails."""
        # Mock database connection error
        mock_get_engine.side_effect = Exception("Connection refused")

        result = check_database()

        assert result == "error"

    @patch("src.api.routes.health.get_engine")
    def test_database_error_query_failed(self, mock_get_engine):
        """Test database check returns 'error' when query execution fails."""
        # Mock successful connection but failed query
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Query failed")

        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        result = check_database()

        assert result == "error"


class TestCheckGeminiAPI:
    """Test Gemini API availability check."""

    @patch("src.config.get_settings")
    def test_gemini_api_ok(self, mock_get_settings):
        """Test Gemini API check returns 'ok' when API key is configured."""
        # Mock settings with valid API key
        mock_settings = MagicMock()
        mock_settings.gemini_api_key = "test_api_key_1234567890"
        mock_get_settings.return_value = mock_settings

        result = check_gemini_api()

        assert result == "ok"

    @patch("src.config.get_settings")
    def test_gemini_api_error_no_key(self, mock_get_settings):
        """Test Gemini API check returns 'error' when API key is missing."""
        # Mock settings with empty API key
        mock_settings = MagicMock()
        mock_settings.gemini_api_key = ""
        mock_get_settings.return_value = mock_settings

        result = check_gemini_api()

        assert result == "error"

    @patch("src.config.get_settings")
    def test_gemini_api_error_exception(self, mock_get_settings):
        """Test Gemini API check returns 'error' when exception occurs."""
        # Mock settings that raises exception
        mock_get_settings.side_effect = Exception("Configuration error")

        result = check_gemini_api()

        assert result == "error"


# ============================================================================
# ENDPOINT TESTS
# ============================================================================


class TestHealthCheckEndpoint:
    """Test health check endpoint."""

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_all_ok(self, mock_check_db, mock_check_gemini):
        """Test health check returns 'ok' when all services are healthy."""
        # Mock all checks as successful
        mock_check_db.return_value = "ok"
        mock_check_gemini.return_value = "ok"

        response = client.get("/api/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "ok"
        assert data["gemini_api"] == "ok"
        assert "timestamp" in data

        # Validate timestamp is ISO 8601
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert timestamp.tzinfo is not None

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_database_error(self, mock_check_db, mock_check_gemini):
        """Test health check returns 'degraded' when database fails."""
        # Mock database as failed
        mock_check_db.return_value = "error"
        mock_check_gemini.return_value = "ok"

        response = client.get("/api/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "error"
        assert data["gemini_api"] == "ok"

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_gemini_error(self, mock_check_db, mock_check_gemini):
        """Test health check returns 'degraded' when Gemini API fails."""
        # Mock Gemini API as failed
        mock_check_db.return_value = "ok"
        mock_check_gemini.return_value = "error"

        response = client.get("/api/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "ok"
        assert data["gemini_api"] == "error"

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_gemini_rate_limited(self, mock_check_db, mock_check_gemini):
        """Test health check returns 'degraded' when Gemini API is rate limited."""
        # Mock Gemini API as rate limited
        mock_check_db.return_value = "ok"
        mock_check_gemini.return_value = "rate_limited"

        response = client.get("/api/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "ok"
        assert data["gemini_api"] == "rate_limited"

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_all_error(self, mock_check_db, mock_check_gemini):
        """Test health check returns 'degraded' when all services fail."""
        # Mock all checks as failed
        mock_check_db.return_value = "error"
        mock_check_gemini.return_value = "error"

        response = client.get("/api/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "error"
        assert data["gemini_api"] == "error"

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_response_schema(self, mock_check_db, mock_check_gemini):
        """Test health check response matches expected schema."""
        # Mock all checks as successful
        mock_check_db.return_value = "ok"
        mock_check_gemini.return_value = "ok"

        response = client.get("/api/health")

        assert response.status_code == 200

        data = response.json()

        # Validate required fields exist
        assert "status" in data
        assert "database" in data
        assert "gemini_api" in data
        assert "timestamp" in data

        # Validate field values match enum constraints
        assert data["status"] in ["ok", "degraded"]
        assert data["database"] in ["ok", "error"]
        assert data["gemini_api"] in ["ok", "error", "rate_limited"]

        # Validate timestamp is a valid ISO 8601 string
        assert isinstance(data["timestamp"], str)
        # Should not raise exception if valid ISO format
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

    @patch("src.api.routes.health.check_gemini_api")
    @patch("src.api.routes.health.check_database")
    def test_health_check_timestamp_format(self, mock_check_db, mock_check_gemini):
        """Test health check timestamp is in ISO 8601 format with timezone."""
        mock_check_db.return_value = "ok"
        mock_check_gemini.return_value = "ok"

        response = client.get("/api/health")

        data = response.json()
        timestamp_str = data["timestamp"]

        # Parse timestamp and verify it's recent (within last minute)
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        time_diff = abs((now - timestamp).total_seconds())

        assert time_diff < 60, "Timestamp should be recent (within 1 minute)"
        assert timestamp.tzinfo is not None, "Timestamp should include timezone"
