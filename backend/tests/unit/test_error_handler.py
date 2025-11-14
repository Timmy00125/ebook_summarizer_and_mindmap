"""Unit tests for error handling framework."""

import asyncio
import logging
import time
from typing import Any

import pytest

from src.utils.error_handler import (
    AppError,
    ErrorCode,
    GracefulDegradation,
    get_status_code,
    retry_with_backoff,
)


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_error_code_values(self):
        """Test that all error codes have correct string values."""
        assert ErrorCode.INVALID_PDF.value == "INVALID_PDF"
        assert ErrorCode.FILE_TOO_LARGE.value == "FILE_TOO_LARGE"
        assert ErrorCode.RATE_LIMITED.value == "RATE_LIMITED"
        assert ErrorCode.TIMEOUT.value == "TIMEOUT"
        assert ErrorCode.DB_ERROR.value == "DB_ERROR"

    def test_error_code_membership(self):
        """Test that all required error codes exist."""
        required_codes = [
            "INVALID_PDF",
            "FILE_TOO_LARGE",
            "RATE_LIMITED",
            "TIMEOUT",
            "DB_ERROR",
            "UNSUPPORTED_FILE_TYPE",
            "FILE_CORRUPTED",
            "API_ERROR",
            "PARSING_ERROR",
            "VALIDATION_ERROR",
        ]
        error_code_values = [code.value for code in ErrorCode]
        for code in required_codes:
            assert code in error_code_values

    def test_error_code_is_string_enum(self):
        """Test that ErrorCode is a string enum."""
        assert isinstance(ErrorCode.INVALID_PDF, str)
        assert isinstance(ErrorCode.RATE_LIMITED, str)


class TestAppError:
    """Test AppError custom exception class."""

    def test_app_error_initialization(self):
        """Test basic AppError initialization."""
        error = AppError(
            error_code=ErrorCode.INVALID_PDF,
            message="Invalid PDF file",
            details={"filename": "test.pdf"},
            status_code=400,
            is_retryable=False,
        )

        assert error.error_code == ErrorCode.INVALID_PDF
        assert error.message == "Invalid PDF file"
        assert error.details == {"filename": "test.pdf"}
        assert error.status_code == 400
        assert error.is_retryable is False

    def test_app_error_default_values(self):
        """Test AppError with default values."""
        error = AppError(error_code=ErrorCode.DB_ERROR, message="Database error")

        assert error.error_code == ErrorCode.DB_ERROR
        assert error.message == "Database error"
        assert error.details == {}
        assert error.status_code == 500
        assert error.is_retryable is False

    def test_app_error_to_dict(self):
        """Test AppError serialization to dictionary."""
        error = AppError(
            error_code=ErrorCode.FILE_TOO_LARGE,
            message="File exceeds 100MB",
            details={"size": 150000000, "limit": 100000000},
        )

        error_dict = error.to_dict()
        assert error_dict == {
            "error_code": "FILE_TOO_LARGE",
            "message": "File exceeds 100MB",
            "details": {"size": 150000000, "limit": 100000000},
        }

    def test_app_error_str_representation(self):
        """Test AppError string representation."""
        error = AppError(
            error_code=ErrorCode.TIMEOUT,
            message="Request timed out",
            details={"timeout_seconds": 30},
        )

        error_str = str(error)
        assert "TIMEOUT" in error_str
        assert "Request timed out" in error_str
        assert "timeout_seconds" in error_str

    def test_app_error_repr(self):
        """Test AppError detailed representation."""
        error = AppError(
            error_code=ErrorCode.RATE_LIMITED,
            message="Rate limit exceeded",
            status_code=429,
            is_retryable=True,
        )

        error_repr = repr(error)
        assert "AppError" in error_repr
        assert "RATE_LIMITED" in error_repr
        assert "429" in error_repr
        assert "is_retryable=True" in error_repr

    def test_app_error_inheritance(self):
        """Test that AppError is an Exception subclass."""
        error = AppError(error_code=ErrorCode.INTERNAL_ERROR, message="Internal error")
        assert isinstance(error, Exception)

    def test_app_error_can_be_raised(self):
        """Test that AppError can be raised and caught."""
        with pytest.raises(AppError) as exc_info:
            raise AppError(
                error_code=ErrorCode.VALIDATION_ERROR, message="Validation failed"
            )

        assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR
        assert exc_info.value.message == "Validation failed"


class TestRetryWithBackoff:
    """Test retry_with_backoff decorator."""

    def test_retry_sync_success_first_attempt(self):
        """Test retry decorator with successful first attempt (sync)."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_sync_success_after_retries(self):
        """Test retry decorator succeeding after retries (sync)."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise AppError(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Rate limited",
                    is_retryable=True,
                )
            return "success"

        result = eventually_successful()
        assert result == "success"
        assert call_count == 3

    def test_retry_sync_exhausts_retries(self):
        """Test retry decorator exhausting all retries (sync)."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise AppError(
                error_code=ErrorCode.RATE_LIMITED,
                message="Rate limited",
                is_retryable=True,
            )

        with pytest.raises(AppError):
            always_fails()

        assert call_count == 3  # Initial + 2 retries

    def test_retry_sync_non_retryable_error(self):
        """Test retry decorator with non-retryable error (sync)."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def non_retryable_error():
            nonlocal call_count
            call_count += 1
            raise AppError(
                error_code=ErrorCode.INVALID_PDF,
                message="Invalid PDF",
                is_retryable=False,
            )

        with pytest.raises(AppError):
            non_retryable_error()

        assert call_count == 1  # Should not retry

    @pytest.mark.asyncio
    async def test_retry_async_success_first_attempt(self):
        """Test retry decorator with successful first attempt (async)."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        async def successful_async_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_async_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_success_after_retries(self):
        """Test retry decorator succeeding after retries (async)."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        async def eventually_successful_async():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise AppError(
                    error_code=ErrorCode.TIMEOUT,
                    message="Timeout",
                    is_retryable=True,
                )
            return "success"

        result = await eventually_successful_async()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_exhausts_retries(self):
        """Test retry decorator exhausting all retries (async)."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        async def always_fails_async():
            nonlocal call_count
            call_count += 1
            raise AppError(
                error_code=ErrorCode.API_ERROR, message="API error", is_retryable=True
            )

        with pytest.raises(AppError):
            await always_fails_async()

        assert call_count == 3  # Initial + 2 retries

    def test_retry_exponential_backoff_timing(self):
        """Test that retry delays follow exponential backoff."""
        call_times = []

        @retry_with_backoff(max_retries=3, initial_delay=0.1, exponential_base=2.0)
        def timed_failures():
            call_times.append(time.time())
            if len(call_times) < 4:
                raise AppError(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Rate limited",
                    is_retryable=True,
                )
            return "success"

        timed_failures()

        # Check delays between calls (allowing some tolerance)
        delays = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]
        assert len(delays) == 3
        # First delay ~0.1s, second ~0.2s, third ~0.4s
        assert 0.08 < delays[0] < 0.15
        assert 0.18 < delays[1] < 0.25
        assert 0.38 < delays[2] < 0.50

    def test_retry_max_delay_cap(self):
        """Test that retry delay is capped at max_delay."""
        call_times = []

        @retry_with_backoff(
            max_retries=5, initial_delay=1.0, max_delay=2.0, exponential_base=2.0
        )
        def capped_delays():
            call_times.append(time.time())
            if len(call_times) < 4:
                raise AppError(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Rate limited",
                    is_retryable=True,
                )
            return "success"

        capped_delays()

        delays = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]
        # Later delays should be capped at max_delay (2.0s)
        for delay in delays[1:]:  # Skip first delay
            assert delay <= 2.1  # Allow small tolerance

    def test_retry_with_custom_exceptions(self):
        """Test retry with custom exception types."""
        call_count = 0

        @retry_with_backoff(
            max_retries=2, initial_delay=0.1, exceptions=(ValueError, TypeError)
        )
        def custom_exception_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Custom error")
            return "success"

        result = custom_exception_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_with_on_retry_callback(self):
        """Test retry with on_retry callback."""
        retry_info = []

        def on_retry_callback(exception: Exception, attempt: int, delay: float):
            retry_info.append(
                {"exception": exception, "attempt": attempt, "delay": delay}
            )

        @retry_with_backoff(
            max_retries=2, initial_delay=0.1, on_retry=on_retry_callback
        )
        def func_with_callback():
            if len(retry_info) < 2:
                raise AppError(
                    error_code=ErrorCode.TIMEOUT, message="Timeout", is_retryable=True
                )
            return "success"

        func_with_callback()

        assert len(retry_info) == 2
        assert retry_info[0]["attempt"] == 1
        assert retry_info[1]["attempt"] == 2

    def test_retry_with_retryable_error_codes(self):
        """Test retry only for specific error codes."""
        call_count = 0

        @retry_with_backoff(
            max_retries=3,
            initial_delay=0.1,
            retryable_error_codes={ErrorCode.RATE_LIMITED},
        )
        def specific_code_retry():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # This should be retried
                raise AppError(
                    error_code=ErrorCode.RATE_LIMITED, message="Rate limited"
                )
            elif call_count == 2:
                # This should NOT be retried
                raise AppError(error_code=ErrorCode.TIMEOUT, message="Timeout")

        with pytest.raises(AppError) as exc_info:
            specific_code_retry()

        assert exc_info.value.error_code == ErrorCode.TIMEOUT
        assert call_count == 2  # Initial call + 1 retry for RATE_LIMITED


class TestGracefulDegradation:
    """Test GracefulDegradation utilities."""

    def test_with_fallback_success(self):
        """Test with_fallback when function succeeds."""

        def successful_func():
            return "success"

        wrapped = GracefulDegradation.with_fallback(
            successful_func, fallback_value="fallback"
        )
        result = wrapped()
        assert result == "success"

    def test_with_fallback_on_error(self):
        """Test with_fallback returns fallback on error."""

        def failing_func():
            raise ValueError("Error")

        wrapped = GracefulDegradation.with_fallback(
            failing_func, fallback_value="fallback", exceptions=(ValueError,)
        )
        result = wrapped()
        assert result == "fallback"

    def test_with_fallback_specific_exceptions(self):
        """Test with_fallback only catches specific exceptions."""

        def failing_func():
            raise TypeError("Type error")

        wrapped = GracefulDegradation.with_fallback(
            failing_func, fallback_value="fallback", exceptions=(ValueError,)
        )

        with pytest.raises(TypeError):
            wrapped()

    @pytest.mark.asyncio
    async def test_with_fallback_async_success(self):
        """Test with_fallback_async when function succeeds."""

        async def successful_async():
            return "success"

        result = await GracefulDegradation.with_fallback_async(
            successful_async, fallback_value="fallback"
        )
        assert result == "success"

    @pytest.mark.asyncio
    async def test_with_fallback_async_on_error(self):
        """Test with_fallback_async returns fallback on error."""

        async def failing_async():
            raise ValueError("Error")

        result = await GracefulDegradation.with_fallback_async(
            failing_async, fallback_value="fallback", exceptions=(ValueError,)
        )
        assert result == "fallback"


class TestGetStatusCode:
    """Test HTTP status code mapping."""

    def test_get_status_code_400_errors(self):
        """Test 400 Bad Request status codes."""
        assert get_status_code(ErrorCode.INVALID_PDF) == 400
        assert get_status_code(ErrorCode.FILE_TOO_LARGE) == 400
        assert get_status_code(ErrorCode.VALIDATION_ERROR) == 400

    def test_get_status_code_404_errors(self):
        """Test 404 Not Found status codes."""
        assert get_status_code(ErrorCode.FILE_NOT_FOUND) == 404
        assert get_status_code(ErrorCode.RECORD_NOT_FOUND) == 404

    def test_get_status_code_409_errors(self):
        """Test 409 Conflict status codes."""
        assert get_status_code(ErrorCode.DUPLICATE_RECORD) == 409
        assert get_status_code(ErrorCode.DOCUMENT_NOT_READY) == 409

    def test_get_status_code_429_errors(self):
        """Test 429 Too Many Requests status codes."""
        assert get_status_code(ErrorCode.RATE_LIMITED) == 429
        assert get_status_code(ErrorCode.QUOTA_EXCEEDED) == 429

    def test_get_status_code_500_errors(self):
        """Test 500 Internal Server Error status codes."""
        assert get_status_code(ErrorCode.DB_ERROR) == 500
        assert get_status_code(ErrorCode.INTERNAL_ERROR) == 500
        assert get_status_code(ErrorCode.PARSING_ERROR) == 500

    def test_get_status_code_504_errors(self):
        """Test 504 Gateway Timeout status codes."""
        assert get_status_code(ErrorCode.TIMEOUT) == 504
        assert get_status_code(ErrorCode.PROCESSING_TIMEOUT) == 504

    def test_get_status_code_502_errors(self):
        """Test 502 Bad Gateway status codes."""
        assert get_status_code(ErrorCode.API_ERROR) == 502

    def test_get_status_code_401_errors(self):
        """Test 401 Unauthorized status codes."""
        assert get_status_code(ErrorCode.AUTH_ERROR) == 401


class TestErrorHandlerIntegration:
    """Integration tests for error handling framework."""

    @pytest.mark.asyncio
    async def test_complete_error_flow_async(self):
        """Test complete error handling flow with async function."""
        call_count = 0

        @retry_with_backoff(
            max_retries=2,
            initial_delay=0.1,
            retryable_error_codes={ErrorCode.RATE_LIMITED},
        )
        async def complex_operation():
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                raise AppError(
                    error_code=ErrorCode.RATE_LIMITED,
                    message="Rate limit exceeded",
                    details={"retry_after": 1},
                    status_code=429,
                    is_retryable=True,
                )
            elif call_count == 2:
                raise AppError(
                    error_code=ErrorCode.TIMEOUT,
                    message="Operation timed out",
                    status_code=504,
                    is_retryable=True,
                )
            return {"result": "success", "attempts": call_count}

        result = await complex_operation()
        assert result["result"] == "success"
        assert call_count == 3

    def test_complete_error_flow_sync(self):
        """Test complete error handling flow with sync function."""
        errors = []

        def on_retry(exception: Exception, attempt: int, delay: float):
            errors.append({"exception": exception, "attempt": attempt, "delay": delay})

        @retry_with_backoff(max_retries=2, initial_delay=0.1, on_retry=on_retry)
        def operation_with_logging():
            if len(errors) < 2:
                raise AppError(
                    error_code=ErrorCode.DB_CONNECTION_ERROR,
                    message="Database connection failed",
                    is_retryable=True,
                )
            return "connected"

        result = operation_with_logging()
        assert result == "connected"
        assert len(errors) == 2
        assert errors[0]["attempt"] == 1
        assert errors[1]["attempt"] == 2
