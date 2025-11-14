"""Health check endpoint for monitoring service status.

This endpoint provides:
- Overall service health status (ok/degraded)
- Database connectivity check
- Gemini API availability check
- ISO 8601 timestamp of the check

Used by:
- Load balancers for routing decisions
- Monitoring systems for alerting
- Deployment pipelines for readiness checks
"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from src.models import get_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create router for health endpoints
router = APIRouter(prefix="/health", tags=["Health"])


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response model per backend-api.yaml contract.

    Attributes:
        status: Overall service health (ok if all checks pass, degraded otherwise)
        database: Database connectivity status
        gemini_api: Gemini API availability status
        timestamp: ISO 8601 timestamp of the health check
    """

    status: Literal["ok", "degraded"] = Field(
        ...,
        description="Overall service health status",
    )
    database: Literal["ok", "error"] = Field(
        ...,
        description="Database connectivity status",
    )
    gemini_api: Literal["ok", "error", "rate_limited"] = Field(
        ...,
        description="Gemini API availability status",
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of the health check",
    )


# ============================================================================
# HEALTH CHECK HELPERS
# ============================================================================


def check_database() -> Literal["ok", "error"]:
    """Check database connectivity.

    Attempts a simple SELECT 1 query to verify the database is reachable
    and accepting queries. Uses connection pooling with pre-ping enabled.

    Returns:
        "ok" if database is accessible, "error" otherwise

    Example:
        >>> status = check_database()
        >>> assert status in ("ok", "error")
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Simple query to verify database is responsive
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        logger.debug("Database health check passed")
        return "ok"

    except Exception as e:
        logger.error(
            "Database health check failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        return "error"


def check_gemini_api() -> Literal["ok", "error", "rate_limited"]:
    """Check Gemini API availability.

    For Phase 2 (Foundational), this is a placeholder that returns "ok".
    In later phases (User Story 2), this will be replaced with an actual
    API call to verify the Gemini API is accessible and not rate-limited.

    Returns:
        "ok" if API is available
        "rate_limited" if API quota is exceeded
        "error" if API is unreachable or authentication failed

    Note:
        This is a minimal check. Full implementation will be added in T064
        when the Gemini service is implemented.
    """
    try:
        # TODO (T064): Replace with actual Gemini API health check
        # For now, just verify the API key is configured
        from src.config import get_settings

        settings = get_settings()
        if settings.gemini_api_key and len(settings.gemini_api_key) > 0:
            logger.debug("Gemini API health check passed (placeholder)")
            return "ok"
        else:
            logger.warning("Gemini API key not configured")
            return "error"

    except Exception as e:
        logger.error(
            "Gemini API health check failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        return "error"


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="API health check",
    description=(
        "Returns the health status of the API and its dependencies. "
        "Used by load balancers and monitoring systems. "
        "Always returns 200 OK with status details in the response body."
    ),
)
async def health_check() -> HealthCheckResponse:
    """Perform comprehensive health check of all service dependencies.

    This endpoint checks:
    - Database connectivity (PostgreSQL)
    - Gemini API availability (placeholder for now)

    The overall status is:
    - "ok": All checks passed
    - "degraded": One or more checks failed

    Returns:
        HealthCheckResponse: Health status of all components

    Example Response:
        {
            "status": "ok",
            "database": "ok",
            "gemini_api": "ok",
            "timestamp": "2025-01-14T12:34:56.789Z"
        }
    """
    logger.info("Health check requested")

    # Perform checks
    db_status = check_database()
    gemini_status = check_gemini_api()

    # Determine overall status
    overall_status: Literal["ok", "degraded"] = (
        "ok" if db_status == "ok" and gemini_status == "ok" else "degraded"
    )

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Log result
    logger.info(
        "Health check completed",
        overall_status=overall_status,
        database=db_status,
        gemini_api=gemini_status,
    )

    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        gemini_api=gemini_status,
        timestamp=timestamp,
    )
