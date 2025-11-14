"""Configuration management using Pydantic BaseSettings.

This module loads and validates all application settings from environment
variables and .env files. It provides type-safe access to configuration
with sensible defaults and clear validation errors.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable loading and validation.

    All settings can be provided via:
    1. Environment variables (highest priority)
    2. .env file in backend directory
    3. Default values (where applicable)

    Required settings without defaults will raise validation errors if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================================
    # SERVER CONFIGURATION
    # ============================================================================

    server_host: str = Field(
        default="0.0.0.0",
        description="Server host address",
    )

    server_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port number",
    )

    env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment mode",
    )

    debug: bool = Field(
        default=True,
        description="Enable debug mode (should be False in production)",
    )

    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================

    database_url: PostgresDsn = Field(
        ...,
        description=(
            "PostgreSQL connection string (required). "
            "Format: postgresql://username:password@host:port/database_name"
        ),
    )

    db_pool_size: int = Field(
        default=20,
        ge=1,
        description="Database connection pool size",
    )

    db_pool_max_overflow: int = Field(
        default=10,
        ge=0,
        description="Maximum overflow connections in pool",
    )

    db_pool_timeout: int = Field(
        default=30,
        ge=1,
        description="Connection pool timeout in seconds",
    )

    db_echo: bool = Field(
        default=False,
        description="Enable SQL logging for debugging",
    )

    # ============================================================================
    # GEMINI API CONFIGURATION
    # ============================================================================

    gemini_api_key: str = Field(
        ...,
        min_length=1,
        description=(
            "Google Generative AI API Key (required). "
            "Get from: https://makersuite.google.com/app/apikey"
        ),
    )

    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model name for summaries and mindmaps",
    )

    gemini_rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        description="Maximum Gemini API requests per minute",
    )

    gemini_request_timeout: int = Field(
        default=30,
        ge=1,
        description="Request timeout for Gemini API calls in seconds",
    )

    gemini_mindmap_timeout: int = Field(
        default=20,
        ge=1,
        description="Timeout for mindmap generation in seconds",
    )

    gemini_summary_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Temperature for summary generation (0.0-1.0)",
    )

    gemini_mindmap_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Temperature for mindmap generation (0.0-1.0)",
    )

    gemini_max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retries for failed API calls",
    )

    gemini_retry_delay: int = Field(
        default=1,
        ge=1,
        description="Initial retry delay in seconds (exponential backoff)",
    )

    # ============================================================================
    # FILE UPLOAD CONFIGURATION
    # ============================================================================

    max_upload_size_bytes: int = Field(
        default=104857600,  # 100MB
        ge=1,
        description="Maximum file size for uploads in bytes",
    )

    upload_dir: Path = Field(
        default=Path("./uploads"),
        description="Directory to store uploaded PDF files",
    )

    temp_dir: Path = Field(
        default=Path("./temp"),
        description="Directory for temporary files during processing",
    )

    # ============================================================================
    # CACHE CONFIGURATION
    # ============================================================================

    cache_max_size_mb: int = Field(
        default=1000,
        ge=1,
        description="LRU cache maximum size in MB",
    )

    cache_ttl_seconds: int = Field(
        default=0,
        ge=0,
        description="Cache TTL in seconds (0 = no TTL)",
    )

    redis_enabled: bool = Field(
        default=False,
        description="Enable Redis caching for distributed deployments",
    )

    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL",
    )

    # ============================================================================
    # DOCUMENT RETENTION CONFIGURATION
    # ============================================================================

    document_retention_days: int = Field(
        default=30,
        ge=1,
        description="Document expiration period in days",
    )

    cleanup_job_time: str = Field(
        default="02:00",
        pattern=r"^\d{2}:\d{2}$",
        description="Daily cleanup job time in HH:MM format (UTC)",
    )

    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format",
    )

    app_name: str = Field(
        default="ebook_summary",
        description="Application name for logs",
    )

    # ============================================================================
    # CORS & SECURITY CONFIGURATION
    # ============================================================================

    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # ============================================================================
    # MONITORING & METRICS CONFIGURATION
    # ============================================================================

    metrics_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics endpoint",
    )

    metrics_port: int = Field(
        default=8001,
        ge=1,
        le=65535,
        description="Prometheus metrics port",
    )

    cost_tracking_enabled: bool = Field(
        default=True,
        description="Track cost of Gemini API calls",
    )

    cost_alert_threshold_usd: float = Field(
        default=100.0,
        ge=0.0,
        description="Weekly cost alert threshold in USD",
    )

    # ============================================================================
    # OPTIONAL: USER MANAGEMENT
    # ============================================================================

    multi_user_enabled: bool = Field(
        default=False,
        description="Enable multi-user features",
    )

    default_user_email: str = Field(
        default="user@example.com",
        description="Default user email for single-user mode",
    )

    default_user_name: str = Field(
        default="Default User",
        description="Default user name for single-user mode",
    )

    # ============================================================================
    # OPTIONAL: DEVELOPMENT & TESTING
    # ============================================================================

    mock_gemini: bool = Field(
        default=False,
        description="Enable mock mode for testing without Gemini API",
    )

    seed_database: bool = Field(
        default=False,
        description="Seed database with sample data on startup",
    )

    @field_validator("upload_dir", "temp_dir", mode="after")
    @classmethod
    def ensure_directories_exist(cls, v: Path) -> Path:
        """Create directories if they don't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_cors_origins_list(self) -> list[str]:
        """Get parsed CORS origins as a list.

        Returns:
            List of allowed CORS origin URLs
        """
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    This function uses LRU cache to ensure settings are loaded only once
    and reused across the application.

    Returns:
        Settings instance with all configuration loaded and validated

    Raises:
        ValidationError: If required settings are missing or invalid
    """
    return Settings()
