"""Error handling middleware for FastAPI application.

This module provides comprehensive error handling that:
- Catches all unhandled exceptions
- Converts exceptions to structured JSON responses
- Maps exception types to appropriate HTTP status codes
- Logs errors with full context
- Returns user-friendly error messages
- Integrates with the error handling framework (error_handler.py)

The middleware ensures consistent error responses across all API endpoints
and prevents internal error details from leaking to clients.
"""

import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import Settings
from src.utils.error_handler import AppError, ErrorCode
from src.utils.logger import get_logger

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI, settings: Settings) -> None:
    """Register error handlers for the FastAPI application.

    This function sets up exception handlers for various error types:
    - AppError: Custom application errors with error codes
    - HTTPException: Starlette HTTP exceptions
    - RequestValidationError: Pydantic validation errors
    - SQLAlchemyError: Database errors
    - Exception: Catch-all for unexpected errors

    Args:
        app: FastAPI application instance
        settings: Application settings (for debug mode, logging config)

    Example:
        from fastapi import FastAPI
        from src.config import get_settings
        from src.middleware.error_middleware import setup_error_handlers

        app = FastAPI()
        settings = get_settings()
        setup_error_handlers(app, settings)
    """
    logger.info("Setting up error handlers", debug_mode=settings.debug)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Handle custom application errors (AppError).

        Args:
            request: FastAPI request object
            exc: AppError exception instance

        Returns:
            JSONResponse with structured error information
        """
        # Extract request context for logging
        context = {
            "path": request.url.path,
            "method": request.method,
            "error_code": exc.error_code.value,
            "status_code": exc.status_code,
            "is_retryable": exc.is_retryable,
        }

        # Add request ID if present
        if hasattr(request.state, "request_id"):
            context["request_id"] = request.state.request_id

        # Log error with context
        logger.error(
            f"Application error: {exc.message}",
            **context,
            details=exc.details,
        )

        # Return structured error response
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code.value,
                "message": exc.message,
                "details": exc.details,
                "is_retryable": exc.is_retryable,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions from Starlette/FastAPI.

        Args:
            request: FastAPI request object
            exc: StarletteHTTPException instance

        Returns:
            JSONResponse with error information
        """
        # Map HTTP status codes to error codes
        error_code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTH_ERROR,
            403: ErrorCode.OPERATION_NOT_ALLOWED,
            404: ErrorCode.RECORD_NOT_FOUND,
            413: ErrorCode.FILE_TOO_LARGE,
            429: ErrorCode.RATE_LIMITED,
            500: ErrorCode.INTERNAL_ERROR,
            503: ErrorCode.API_ERROR,
        }

        error_code = error_code_map.get(exc.status_code, ErrorCode.UNKNOWN_ERROR)

        # Log HTTP exception
        logger.warning(
            f"HTTP exception: {exc.detail}",
            path=request.url.path,
            method=request.method,
            status_code=exc.status_code,
            error_code=error_code.value,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": error_code.value,
                "message": str(exc.detail),
                "details": {},
                "is_retryable": exc.status_code in [429, 500, 503],
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors from request body/params.

        Args:
            request: FastAPI request object
            exc: RequestValidationError instance

        Returns:
            JSONResponse with validation error details
        """
        # Extract validation error details
        errors = exc.errors()
        validation_details = [
            {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "value_error"),
            }
            for error in errors
        ]

        # Log validation error
        logger.warning(
            "Request validation error",
            path=request.url.path,
            method=request.method,
            validation_errors=validation_details,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Request validation failed",
                "details": {"validation_errors": validation_details},
                "is_retryable": False,
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors from models.

        Args:
            request: FastAPI request object
            exc: ValidationError instance

        Returns:
            JSONResponse with validation error details
        """
        # Extract validation error details
        errors = exc.errors()
        validation_details = [
            {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "value_error"),
            }
            for error in errors
        ]

        # Log validation error
        logger.warning(
            "Pydantic validation error",
            path=request.url.path,
            method=request.method,
            validation_errors=validation_details,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Data validation failed",
                "details": {"validation_errors": validation_details},
                "is_retryable": False,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """Handle database integrity constraint violations.

        Args:
            request: FastAPI request object
            exc: IntegrityError instance

        Returns:
            JSONResponse with appropriate error code
        """
        error_message = str(exc.orig) if hasattr(exc, "orig") else str(exc)

        # Determine if it's a duplicate record error
        is_duplicate = any(
            keyword in error_message.lower()
            for keyword in ["unique", "duplicate", "already exists"]
        )

        error_code = ErrorCode.DUPLICATE_RECORD if is_duplicate else ErrorCode.DB_ERROR

        # Log database error
        logger.error(
            "Database integrity error",
            path=request.url.path,
            method=request.method,
            error_code=error_code.value,
            error_message=error_message,
        )

        # Return user-friendly message (don't leak SQL details)
        user_message = (
            "A record with this information already exists"
            if is_duplicate
            else "Database constraint violation"
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT
            if is_duplicate
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": error_code.value,
                "message": user_message,
                "details": {} if not settings.debug else {"db_error": error_message},
                "is_retryable": False,
            },
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(
        request: Request, exc: OperationalError
    ) -> JSONResponse:
        """Handle database operational errors (connection, timeout, etc.).

        Args:
            request: FastAPI request object
            exc: OperationalError instance

        Returns:
            JSONResponse with database error information
        """
        error_message = str(exc.orig) if hasattr(exc, "orig") else str(exc)

        # Log database error
        logger.error(
            "Database operational error",
            path=request.url.path,
            method=request.method,
            error_message=error_message,
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error_code": ErrorCode.DB_CONNECTION_ERROR.value,
                "message": "Database connection error",
                "details": {} if not settings.debug else {"db_error": error_message},
                "is_retryable": True,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle generic SQLAlchemy errors.

        Args:
            request: FastAPI request object
            exc: SQLAlchemyError instance

        Returns:
            JSONResponse with database error information
        """
        error_message = str(exc)

        # Log database error
        logger.error(
            "SQLAlchemy error",
            path=request.url.path,
            method=request.method,
            error_message=error_message,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": ErrorCode.DB_ERROR.value,
                "message": "Database error occurred",
                "details": {} if not settings.debug else {"db_error": error_message},
                "is_retryable": True,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all handler for unexpected exceptions.

        This handler ensures that no unhandled exceptions leak to the client
        and all errors are logged properly.

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse with generic error information
        """
        # Log full exception with traceback
        logger.error(
            f"Unhandled exception: {exc}",
            path=request.url.path,
            method=request.method,
            exception_type=type(exc).__name__,
            traceback=traceback.format_exc() if settings.debug else None,
        )

        # Return generic error response (don't leak internal details)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": ErrorCode.INTERNAL_ERROR.value,
                "message": "An unexpected error occurred",
                "details": (
                    {"exception": str(exc), "type": type(exc).__name__}
                    if settings.debug
                    else {}
                ),
                "is_retryable": False,
            },
        )

    logger.info("Error handlers configured successfully")


def get_error_handler_summary() -> dict:
    """Get a summary of registered error handlers for monitoring/debugging.

    Returns:
        Dictionary with error handler configuration
    """
    return {
        "handlers": [
            "AppError",
            "StarletteHTTPException",
            "RequestValidationError",
            "ValidationError",
            "IntegrityError",
            "OperationalError",
            "SQLAlchemyError",
            "Exception (catch-all)",
        ],
        "structured_responses": True,
        "error_code_mapping": True,
        "context_logging": True,
    }
