"""Error handling framework for the ebook summarizer backend.

This module provides:
- ErrorCode enum: Standardized error codes for all error scenarios
- AppError: Custom exception class with structured error information
- retry_with_backoff: Decorator for automatic retry with exponential backoff
- Graceful degradation strategies and structured logging integration
"""

import asyncio
import functools
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

# Type variable for generic function return types
T = TypeVar("T")


class ErrorCode(str, Enum):
    """Standardized error codes for all application errors.

    These error codes are used throughout the application for consistent
    error handling and client-side error message mapping.
    """

    # File upload and validation errors
    INVALID_PDF = "INVALID_PDF"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    DUPLICATE_FILE = "DUPLICATE_FILE"

    # API and rate limiting errors
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    API_ERROR = "API_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"

    # Database errors
    DB_ERROR = "DB_ERROR"
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
    DB_TRANSACTION_ERROR = "DB_TRANSACTION_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"

    # Processing errors
    PARSING_ERROR = "PARSING_ERROR"
    GENERATION_ERROR = "GENERATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"

    # Document state errors
    DOCUMENT_NOT_READY = "DOCUMENT_NOT_READY"
    INVALID_STATE = "INVALID_STATE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"

    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class AppError(Exception):
    """Custom application exception with structured error information.

    This exception class provides consistent error handling across the application
    with support for error codes, detailed messages, and additional context.

    Attributes:
        error_code: Standardized error code from ErrorCode enum
        message: Human-readable error message
        details: Optional dictionary with additional error context
        status_code: HTTP status code for API responses (default: 500)
        is_retryable: Whether this error can be retried (default: False)
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[dict[str, Any]] = None,
        status_code: int = 500,
        is_retryable: bool = False,
    ):
        """Initialize AppError with error information.

        Args:
            error_code: Error code from ErrorCode enum
            message: Human-readable error message
            details: Optional dictionary with additional context
            status_code: HTTP status code (default: 500)
            is_retryable: Whether the operation can be retried (default: False)
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.is_retryable = is_retryable
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON serialization.

        Returns:
            Dictionary with error_code, message, and details
        """
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        """String representation of the error."""
        details_str = f", details={self.details}" if self.details else ""
        return f"{self.error_code.value}: {self.message}{details_str}"

    def __repr__(self) -> str:
        """Detailed representation of the error."""
        return (
            f"AppError(error_code={self.error_code}, message='{self.message}', "
            f"details={self.details}, status_code={self.status_code}, "
            f"is_retryable={self.is_retryable})"
        )


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retryable_error_codes: Optional[set[ErrorCode]] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for automatic retry with exponential backoff.

    This decorator implements retry logic with exponential backoff for both
    synchronous and asynchronous functions. It supports:
    - Configurable retry attempts and delays
    - Exponential backoff with maximum delay cap
    - Selective retry based on exception types or error codes
    - Optional callback on retry attempts
    - Structured logging integration

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay between retries (default: 60.0)
        exponential_base: Base for exponential backoff (default: 2.0)
        exceptions: Tuple of exception types to catch (default: all Exception)
        retryable_error_codes: Set of ErrorCode values to retry (AppError only)
        on_retry: Optional callback function called on each retry attempt

    Returns:
        Decorated function with retry logic

    Example:
        >>> @retry_with_backoff(max_retries=3, initial_delay=1.0)
        ... def api_call():
        ...     # Make API call
        ...     pass

        >>> @retry_with_backoff(
        ...     max_retries=5,
        ...     retryable_error_codes={ErrorCode.RATE_LIMITED, ErrorCode.TIMEOUT}
        ... )
        ... async def gemini_request():
        ...     # Make Gemini API request
        ...     pass
    """
    # Default retryable error codes if not specified
    if retryable_error_codes is None:
        retryable_error_codes = {
            ErrorCode.RATE_LIMITED,
            ErrorCode.TIMEOUT,
            ErrorCode.API_ERROR,
            ErrorCode.DB_CONNECTION_ERROR,
        }

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator wrapper."""

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            """Async function wrapper with retry logic."""
            logger = logging.getLogger(func.__module__)
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Check if this is a retryable error
                    is_retryable = True
                    if isinstance(e, AppError):
                        is_retryable = (
                            e.is_retryable or e.error_code in retryable_error_codes
                        )

                    # If not retryable or out of retries, raise immediately
                    if not is_retryable or attempt >= max_retries:
                        logger.error(
                            f"Operation failed after {attempt + 1} attempts: {e}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt + 1,
                                "error_type": type(e).__name__,
                            },
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base**attempt), max_delay)

                    # Log retry attempt
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s: {e}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "delay": delay,
                            "error_type": type(e).__name__,
                        },
                    )

                    # Call optional retry callback
                    if on_retry:
                        on_retry(e, attempt + 1, delay)

                    # Wait before retry
                    await asyncio.sleep(delay)

            # This should never be reached, but satisfy type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop exit")

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            """Synchronous function wrapper with retry logic."""
            logger = logging.getLogger(func.__module__)
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Check if this is a retryable error
                    is_retryable = True
                    if isinstance(e, AppError):
                        is_retryable = (
                            e.is_retryable or e.error_code in retryable_error_codes
                        )

                    # If not retryable or out of retries, raise immediately
                    if not is_retryable or attempt >= max_retries:
                        logger.error(
                            f"Operation failed after {attempt + 1} attempts: {e}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt + 1,
                                "error_type": type(e).__name__,
                            },
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base**attempt), max_delay)

                    # Log retry attempt
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s: {e}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "delay": delay,
                            "error_type": type(e).__name__,
                        },
                    )

                    # Call optional retry callback
                    if on_retry:
                        on_retry(e, attempt + 1, delay)

                    # Wait before retry
                    time.sleep(delay)

            # This should never be reached, but satisfy type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop exit")

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


# Graceful degradation strategies
class GracefulDegradation:
    """Utilities for graceful degradation strategies.

    Provides methods to handle errors gracefully and return fallback values
    or partial results when operations fail.
    """

    @staticmethod
    def with_fallback(
        func: Callable[..., T],
        fallback_value: T,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        log_errors: bool = True,
    ) -> Callable[..., T]:
        """Execute function with fallback value on error.

        Args:
            func: Function to execute
            fallback_value: Value to return on error
            exceptions: Tuple of exceptions to catch
            log_errors: Whether to log errors (default: True)

        Returns:
            Function result or fallback value
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_errors:
                    logger = logging.getLogger(func.__module__)
                    logger.warning(
                        f"Function {func.__name__} failed, using fallback: {e}",
                        extra={
                            "function": func.__name__,
                            "error_type": type(e).__name__,
                            "fallback_value": str(fallback_value),
                        },
                    )
                return fallback_value

        return wrapper

    @staticmethod
    async def with_fallback_async(
        func: Callable[..., T],
        fallback_value: T,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        log_errors: bool = True,
    ) -> T:
        """Execute async function with fallback value on error.

        Args:
            func: Async function to execute
            fallback_value: Value to return on error
            exceptions: Tuple of exceptions to catch
            log_errors: Whether to log errors (default: True)

        Returns:
            Function result or fallback value
        """
        try:
            return await func()
        except exceptions as e:
            if log_errors:
                logger = logging.getLogger(func.__module__)
                logger.warning(
                    f"Function {func.__name__} failed, using fallback: {e}",
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "fallback_value": str(fallback_value),
                    },
                )
            return fallback_value


# HTTP status code mappings for common errors
ERROR_STATUS_CODES: dict[ErrorCode, int] = {
    # 400 Bad Request
    ErrorCode.INVALID_PDF: 400,
    ErrorCode.FILE_TOO_LARGE: 400,
    ErrorCode.UNSUPPORTED_FILE_TYPE: 400,
    ErrorCode.FILE_CORRUPTED: 400,
    ErrorCode.DUPLICATE_FILE: 400,
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.INVALID_STATE: 400,
    ErrorCode.OPERATION_NOT_ALLOWED: 400,
    # 404 Not Found
    ErrorCode.FILE_NOT_FOUND: 404,
    ErrorCode.RECORD_NOT_FOUND: 404,
    # 409 Conflict
    ErrorCode.DUPLICATE_RECORD: 409,
    ErrorCode.DOCUMENT_NOT_READY: 409,
    # 429 Too Many Requests
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.QUOTA_EXCEEDED: 429,
    # 500 Internal Server Error
    ErrorCode.DB_ERROR: 500,
    ErrorCode.DB_CONNECTION_ERROR: 500,
    ErrorCode.DB_TRANSACTION_ERROR: 500,
    ErrorCode.PARSING_ERROR: 500,
    ErrorCode.GENERATION_ERROR: 500,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.UNKNOWN_ERROR: 500,
    ErrorCode.CONFIGURATION_ERROR: 500,
    # 504 Gateway Timeout
    ErrorCode.TIMEOUT: 504,
    ErrorCode.PROCESSING_TIMEOUT: 504,
    # 502 Bad Gateway
    ErrorCode.API_ERROR: 502,
    # 401 Unauthorized
    ErrorCode.AUTH_ERROR: 401,
}


def get_status_code(error_code: ErrorCode) -> int:
    """Get HTTP status code for an error code.

    Args:
        error_code: ErrorCode enum value

    Returns:
        HTTP status code (default: 500 if not mapped)
    """
    return ERROR_STATUS_CODES.get(error_code, 500)
