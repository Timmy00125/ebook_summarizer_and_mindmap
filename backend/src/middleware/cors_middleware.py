"""CORS (Cross-Origin Resource Sharing) middleware configuration.

This module configures CORS to allow the Next.js frontend to communicate
securely with the FastAPI backend. It handles preflight requests (OPTIONS)
and sets appropriate headers for cross-origin requests.

CORS settings are loaded from the application configuration (config.py)
which reads from environment variables.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Configure CORS middleware for the FastAPI application.

    This function adds CORS middleware to enable secure cross-origin requests
    from the frontend. It supports:
    - Configurable allowed origins (from environment variables)
    - Credentials (cookies, authorization headers)
    - All standard HTTP methods
    - Custom headers for API requests

    Args:
        app: FastAPI application instance
        settings: Application settings with CORS configuration

    Example:
        from fastapi import FastAPI
        from src.config import get_settings
        from src.middleware.cors_middleware import setup_cors

        app = FastAPI()
        settings = get_settings()
        setup_cors(app, settings)
    """
    # Parse CORS origins from settings
    allowed_origins = settings.cors_origins

    # Log CORS configuration for debugging
    logger.info(
        "Setting up CORS middleware",
        allowed_origins=allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        environment=settings.env,
    )

    # Add CORS middleware to FastAPI app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Requested-With",
            "X-Request-ID",
        ],
        expose_headers=[
            "Content-Length",
            "Content-Type",
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

    logger.info("CORS middleware configured successfully")


def get_cors_config_summary(settings: Settings) -> dict:
    """Get a summary of CORS configuration for monitoring/debugging.

    Args:
        settings: Application settings

    Returns:
        Dictionary with CORS configuration summary
    """
    return {
        "allowed_origins": settings.cors_origins,
        "allow_credentials": settings.cors_allow_credentials,
        "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "max_age": 3600,
    }
