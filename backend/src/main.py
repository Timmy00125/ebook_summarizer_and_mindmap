"""FastAPI application initialization and configuration.

This is the main entry point for the backend API. It:
- Creates the FastAPI application instance
- Configures middleware (CORS, error handling)
- Registers API routes
- Sets up database connections
- Configures logging
- Provides health check endpoint
- Handles graceful startup and shutdown

Run with: uvicorn src.main:app --reload
"""

import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.routes import health
from src.config import get_settings
from src.middleware.cors_middleware import setup_cors
from src.middleware.error_middleware import setup_error_handlers
from src.models import init_db
from src.utils.logger import get_logger, setup_logging

# Initialize settings
settings = get_settings()

# Setup logging before anything else
setup_logging(log_level=settings.log_level, log_format=settings.log_format)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application lifespan (startup and shutdown).

    This context manager handles:
    - Startup: Initialize database, logging, connections
    - Shutdown: Close connections, cleanup resources

    Args:
        app: FastAPI application instance

    Yields:
        None during application runtime
    """
    # ========================================================================
    # STARTUP
    # ========================================================================
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        environment=settings.env,
        debug=settings.debug,
        version="1.0.0",
    )

    try:
        # Initialize database connection
        logger.info("Initializing database connection")
        init_db()
        logger.info("Database initialized successfully")

        # Log configuration summary
        logger.info(
            "Application configuration loaded",
            cors_origins=settings.cors_origins,
            max_upload_size_mb=settings.max_upload_size_bytes // (1024 * 1024),
            gemini_model=settings.gemini_model,
            cache_max_size_mb=settings.cache_max_size_mb,
        )

        # Verify required directories exist
        logger.info(
            "Verified required directories",
            upload_dir=str(settings.upload_dir),
            temp_dir=str(settings.temp_dir),
        )

        logger.info("Application startup complete")

    except Exception as e:
        logger.critical(
            "Failed to start application",
            error=str(e),
            error_type=type(e).__name__,
        )
        # Exit on critical startup failure
        sys.exit(1)

    # ========================================================================
    # RUNTIME (Application is running)
    # ========================================================================
    yield

    # ========================================================================
    # SHUTDOWN
    # ========================================================================
    logger.info("Starting graceful shutdown")

    try:
        # Close database connections
        logger.info("Closing database connections")
        # Note: SQLAlchemy engine will handle connection cleanup

        logger.info("Application shutdown complete")

    except Exception as e:
        logger.error(
            "Error during shutdown",
            error=str(e),
            error_type=type(e).__name__,
        )


# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="PDF Summary & Mindmap API",
    description=(
        "Backend API for document processing with AI summaries and mindmaps. "
        "Upload PDF documents, generate summaries and hierarchical mindmaps "
        "using Google Gemini AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)


# ============================================================================
# CONFIGURE MIDDLEWARE
# ============================================================================

# Setup CORS middleware (must be before other middleware)
setup_cors(app, settings)

# Setup error handling middleware
setup_error_handlers(app, settings)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Basic health check endpoint.

    This is a simple endpoint that returns OK if the application is running.
    For detailed health checks (database, Gemini API), see /api/health endpoint.

    Returns:
        JSONResponse with health status

    Example:
        >>> response = await client.get("/health")
        >>> assert response.status_code == 200
        >>> assert response.json()["status"] == "ok"
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "app_name": settings.app_name,
            "environment": settings.env,
            "version": "1.0.0",
        },
    )


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """Root endpoint with API information.

    Returns:
        JSONResponse with API metadata and links
    """
    return JSONResponse(
        status_code=200,
        content={
            "message": "PDF Summary & Mindmap API",
            "version": "1.0.0",
            "docs_url": "/docs" if settings.debug else None,
            "health_check": "/health",
            "detailed_health_check": "/api/health",
        },
    )


# ============================================================================
# REGISTER API ROUTES
# ============================================================================

# Register health check endpoint (detailed)
app.include_router(health.router, prefix="/api")

# TODO: Register additional route modules here as they are created:
# Example:
# from src.api.routes import documents, summaries, mindmaps
# app.include_router(documents.router, prefix="/api", tags=["Documents"])
# app.include_router(summaries.router, prefix="/api", tags=["Summaries"])
# app.include_router(mindmaps.router, prefix="/api", tags=["Mindmaps"])


# ============================================================================
# MAIN ENTRY POINT (for direct execution)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn programmatically (for development only)
    logger.info(
        "Starting development server",
        host=settings.server_host,
        port=settings.server_port,
    )

    uvicorn.run(
        "src.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_config=None,  # Use our custom logging setup
        access_log=settings.debug,
    )
