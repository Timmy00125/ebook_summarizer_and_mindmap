"""Unit tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config import Settings, get_settings


class TestSettings:
    """Test suite for Settings configuration class."""

    def test_settings_with_minimal_required_fields(self, tmp_path):
        """Test settings loads with only required fields provided."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key-12345",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            # Verify required fields
            assert str(settings.database_url) == env_vars["DATABASE_URL"]
            assert settings.gemini_api_key == env_vars["GEMINI_API_KEY"]

            # Verify defaults are applied
            assert settings.server_host == "0.0.0.0"
            assert settings.server_port == 8000
            assert settings.env == "development"
            assert settings.debug is True
            assert settings.gemini_model == "gemini-1.5-flash"

    def test_settings_missing_database_url_raises_error(self):
        """Test that missing DATABASE_URL raises validation error."""
        env_vars = {
            "GEMINI_API_KEY": "test-api-key-12345",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert "DATABASE_URL" in error_msg or "database_url" in error_msg

    def test_settings_missing_gemini_api_key_raises_error(self):
        """Test that missing GEMINI_API_KEY raises validation error."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert "GEMINI_API_KEY" in error_msg or "gemini_api_key" in error_msg

    def test_settings_custom_values_override_defaults(self, tmp_path):
        """Test that custom environment values override defaults."""
        env_vars = {
            "DATABASE_URL": "postgresql://custom:pass@db.example.com:5432/mydb",
            "GEMINI_API_KEY": "custom-api-key",
            "SERVER_HOST": "127.0.0.1",
            "SERVER_PORT": "9000",
            "ENV": "production",
            "DEBUG": "false",
            "GEMINI_MODEL": "gemini-1.5-pro",
            "LOG_LEVEL": "WARNING",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.server_host == "127.0.0.1"
            assert settings.server_port == 9000
            assert settings.env == "production"
            assert settings.debug is False
            assert settings.gemini_model == "gemini-1.5-pro"
            assert settings.log_level == "WARNING"

    def test_settings_port_validation(self, tmp_path):
        """Test that invalid port numbers are rejected."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "SERVER_PORT": "99999",  # Invalid port
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert "server_port" in error_msg.lower()

    def test_settings_temperature_validation(self, tmp_path):
        """Test that temperature values are validated (0.0-1.0 range)."""
        # Test invalid temperature > 1.0
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "GEMINI_SUMMARY_TEMPERATURE": "1.5",  # Invalid
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert "gemini_summary_temperature" in error_msg.lower()

    def test_settings_cors_origins_parsing(self, tmp_path):
        """Test that CORS origins are properly parsed from comma-separated string."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "CORS_ORIGINS": "http://localhost:3000,https://app.example.com,https://www.example.com",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            origins = settings.get_cors_origins_list()
            assert len(origins) == 3
            assert "http://localhost:3000" in origins
            assert "https://app.example.com" in origins
            assert "https://www.example.com" in origins

    def test_settings_cors_origins_with_spaces(self, tmp_path):
        """Test that CORS origins handle spaces correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "CORS_ORIGINS": " http://localhost:3000 , https://app.example.com ",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            origins = settings.get_cors_origins_list()
            assert len(origins) == 2
            assert "http://localhost:3000" in origins
            assert "https://app.example.com" in origins

    def test_settings_database_pool_configuration(self, tmp_path):
        """Test database pool settings are loaded correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "DB_POOL_SIZE": "50",
            "DB_POOL_MAX_OVERFLOW": "20",
            "DB_POOL_TIMEOUT": "60",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.db_pool_size == 50
            assert settings.db_pool_max_overflow == 20
            assert settings.db_pool_timeout == 60

    def test_settings_gemini_configuration(self, tmp_path):
        """Test Gemini API settings are loaded correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "GEMINI_RATE_LIMIT_PER_MINUTE": "120",
            "GEMINI_REQUEST_TIMEOUT": "45",
            "GEMINI_MINDMAP_TIMEOUT": "25",
            "GEMINI_MAX_RETRIES": "5",
            "GEMINI_RETRY_DELAY": "2",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.gemini_rate_limit_per_minute == 120
            assert settings.gemini_request_timeout == 45
            assert settings.gemini_mindmap_timeout == 25
            assert settings.gemini_max_retries == 5
            assert settings.gemini_retry_delay == 2

    def test_settings_file_upload_configuration(self, tmp_path):
        """Test file upload settings are loaded correctly."""
        custom_upload = tmp_path / "custom_uploads"
        custom_temp = tmp_path / "custom_temp"

        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "MAX_UPLOAD_SIZE_BYTES": "209715200",  # 200MB
            "UPLOAD_DIR": str(custom_upload),
            "TEMP_DIR": str(custom_temp),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.max_upload_size_bytes == 209715200
            assert settings.upload_dir == custom_upload
            assert settings.temp_dir == custom_temp
            # Directories should be created
            assert custom_upload.exists()
            assert custom_temp.exists()

    def test_settings_cache_configuration(self, tmp_path):
        """Test cache settings are loaded correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "CACHE_MAX_SIZE_MB": "2000",
            "CACHE_TTL_SECONDS": "3600",
            "REDIS_ENABLED": "true",
            "REDIS_URL": "redis://localhost:6379/1",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.cache_max_size_mb == 2000
            assert settings.cache_ttl_seconds == 3600
            assert settings.redis_enabled is True
            assert settings.redis_url == "redis://localhost:6379/1"

    def test_settings_monitoring_configuration(self, tmp_path):
        """Test monitoring and metrics settings are loaded correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "METRICS_ENABLED": "false",
            "METRICS_PORT": "9090",
            "COST_TRACKING_ENABLED": "false",
            "COST_ALERT_THRESHOLD_USD": "500.50",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.metrics_enabled is False
            assert settings.metrics_port == 9090
            assert settings.cost_tracking_enabled is False
            assert settings.cost_alert_threshold_usd == 500.50

    def test_settings_user_management_configuration(self, tmp_path):
        """Test user management settings are loaded correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "MULTI_USER_ENABLED": "true",
            "DEFAULT_USER_EMAIL": "admin@example.com",
            "DEFAULT_USER_NAME": "Admin User",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.multi_user_enabled is True
            assert settings.default_user_email == "admin@example.com"
            assert settings.default_user_name == "Admin User"

    def test_settings_development_configuration(self, tmp_path):
        """Test development and testing settings are loaded correctly."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "MOCK_GEMINI": "true",
            "SEED_DATABASE": "true",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.mock_gemini is True
            assert settings.seed_database is True

    def test_settings_cleanup_job_time_validation(self, tmp_path):
        """Test cleanup job time format validation."""
        # Valid format
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "CLEANUP_JOB_TIME": "03:30",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert settings.cleanup_job_time == "03:30"

        # Invalid format
        env_vars["CLEANUP_JOB_TIME"] = "3:30"  # Missing leading zero

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_env_literal_validation(self, tmp_path):
        """Test that ENV field only accepts valid literal values."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "ENV": "invalid_env",  # Not in allowed literals
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_log_level_literal_validation(self, tmp_path):
        """Test that LOG_LEVEL field only accepts valid literal values."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "LOG_LEVEL": "TRACE",  # Not a valid log level
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()


class TestGetSettings:
    """Test suite for get_settings function."""

    def test_get_settings_returns_cached_instance(self, tmp_path):
        """Test that get_settings returns the same cached instance."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "GEMINI_API_KEY": "test-api-key",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "TEMP_DIR": str(tmp_path / "temp"),
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Clear the cache first
            get_settings.cache_clear()

            settings1 = get_settings()
            settings2 = get_settings()

            # Should be the same instance due to caching
            assert settings1 is settings2

    def test_get_settings_raises_on_missing_required_fields(self):
        """Test that get_settings raises ValidationError for missing fields."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear the cache first
            get_settings.cache_clear()

            with pytest.raises(ValidationError):
                get_settings()
