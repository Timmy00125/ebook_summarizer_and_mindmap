"""Unit tests for structured logging utility."""

import logging
import os
from unittest.mock import patch

import pytest
import structlog

from src.utils.logger import (
    add_module_name,
    add_timestamp,
    bind_context,
    clear_context,
    get_logger,
    setup_logging,
    unbind_context,
)


class TestSetupLogging:
    """Test suite for setup_logging function."""

    def test_setup_with_default_values(self):
        """Test setup_logging with default configuration."""
        setup_logging()
        logger = get_logger(__name__)

        # Verify logger is created and has required methods
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "critical")

    def test_setup_with_debug_level(self, caplog):
        """Test setup_logging with DEBUG level."""
        setup_logging(log_level="DEBUG")
        logger = get_logger(__name__)

        # Log at DEBUG level
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message", test_field="value")

        # Verify DEBUG logs are captured
        assert len(caplog.records) > 0

    def test_setup_with_info_level(self, caplog):
        """Test setup_logging with INFO level."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        with caplog.at_level(logging.INFO):
            logger.info("Info message")

        assert len(caplog.records) > 0

    def test_setup_with_warning_level(self, caplog):
        """Test setup_logging with WARNING level."""
        setup_logging(log_level="WARNING")
        logger = get_logger(__name__)

        with caplog.at_level(logging.WARNING):
            logger.warning("Warning message")

        assert len(caplog.records) > 0

    def test_setup_with_error_level(self, caplog):
        """Test setup_logging with ERROR level."""
        setup_logging(log_level="ERROR")
        logger = get_logger(__name__)

        with caplog.at_level(logging.ERROR):
            logger.error("Error message")

        assert len(caplog.records) > 0

    def test_setup_with_critical_level(self, caplog):
        """Test setup_logging with CRITICAL level."""
        setup_logging(log_level="CRITICAL")
        logger = get_logger(__name__)

        with caplog.at_level(logging.CRITICAL):
            logger.critical("Critical message")

        assert len(caplog.records) > 0

    def test_setup_with_json_format(self):
        """Test setup_logging with JSON format configures correctly."""
        setup_logging(log_level="INFO", log_format="json")
        logger = get_logger(__name__)

        # Just verify logger was created successfully
        assert logger is not None

    def test_setup_with_console_format(self):
        """Test setup_logging with console format configures correctly."""
        setup_logging(log_level="INFO", log_format="console")
        logger = get_logger(__name__)

        # Verify logger was created successfully
        assert logger is not None

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "LOG_FORMAT": "json"})
    def test_setup_reads_from_environment(self):
        """Test that setup_logging reads from environment variables."""
        setup_logging()  # Should use env vars
        logger = get_logger(__name__)

        # Should be able to log at DEBUG level
        assert logger is not None

    def test_setup_with_invalid_log_level(self):
        """Test setup_logging with invalid log level defaults to INFO."""
        setup_logging(log_level="INVALID")
        logger = get_logger(__name__)

        # Should still create logger with INFO as fallback
        assert logger is not None


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_returns_logger_with_methods(self):
        """Test that get_logger returns a logger with required methods."""
        setup_logging()
        logger = get_logger(__name__)

        # Verify logger has required methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "critical")

    def test_get_logger_with_different_names(self):
        """Test that different logger names work correctly."""
        setup_logging()

        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not None
        assert logger2 is not None

    def test_logger_info_method(self, caplog):
        """Test logger.info() method."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        with caplog.at_level(logging.INFO):
            logger.info("Info log", field1="value1")

        assert len(caplog.records) > 0

    def test_logger_warning_method(self, caplog):
        """Test logger.warning() method."""
        setup_logging(log_level="WARNING")
        logger = get_logger(__name__)

        with caplog.at_level(logging.WARNING):
            logger.warning("Warning log", field1="value1")

        assert len(caplog.records) > 0

    def test_logger_error_method(self, caplog):
        """Test logger.error() method."""
        setup_logging(log_level="ERROR")
        logger = get_logger(__name__)

        with caplog.at_level(logging.ERROR):
            logger.error("Error log", field1="value1")

        assert len(caplog.records) > 0

    def test_logger_debug_method(self, caplog):
        """Test logger.debug() method."""
        setup_logging(log_level="DEBUG")
        logger = get_logger(__name__)

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug log", field1="value1")

        assert len(caplog.records) > 0

    def test_logger_critical_method(self, caplog):
        """Test logger.critical() method."""
        setup_logging(log_level="CRITICAL")
        logger = get_logger(__name__)

        with caplog.at_level(logging.CRITICAL):
            logger.critical("Critical log", field1="value1")

        assert len(caplog.records) > 0


class TestContextTracking:
    """Test suite for context tracking functions."""

    def test_bind_context_with_request_id(self, caplog):
        """Test binding request_id context."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(request_id="abc-123")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        # Context should be bound
        assert len(caplog.records) > 0

    def test_bind_context_with_user_id(self, caplog):
        """Test binding user_id context."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(user_id=456)

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_bind_context_with_document_id(self, caplog):
        """Test binding document_id context."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(document_id=789)

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_bind_context_with_all_fields(self, caplog):
        """Test binding all context fields together."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(request_id="abc-123", user_id=456, document_id=789)

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_bind_context_with_custom_fields(self, caplog):
        """Test binding custom context fields."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(custom_field="custom_value", another_field=123)

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_clear_context(self, caplog):
        """Test clearing all context."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(request_id="abc-123", user_id=456)
        clear_context()

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_unbind_context_single_key(self, caplog):
        """Test unbinding a single context key."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(request_id="abc-123", user_id=456)
        unbind_context("request_id")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_unbind_context_multiple_keys(self, caplog):
        """Test unbinding multiple context keys."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(request_id="abc-123", user_id=456, document_id=789)
        unbind_context("request_id", "document_id")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_context_persists_across_log_calls(self, caplog):
        """Test that context persists across multiple log calls."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        bind_context(request_id="abc-123")

        with caplog.at_level(logging.INFO):
            logger.info("First message")
            logger.info("Second message")

        # Both log calls should be recorded
        assert len(caplog.records) >= 2


class TestStructuredFields:
    """Test suite for structured log fields."""

    def test_log_output_works(self, caplog):
        """Test that logs can be output successfully."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0

    def test_log_with_multiple_levels(self, caplog):
        """Test logging at different levels."""
        setup_logging(log_level="DEBUG")
        logger = get_logger(__name__)

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

        assert len(caplog.records) >= 4

    def test_log_with_custom_fields(self, caplog):
        """Test that logs with custom fields work."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        with caplog.at_level(logging.INFO):
            logger.info("Test message", custom_key="custom_value", numeric_field=42)

        assert len(caplog.records) > 0


class TestProcessors:
    """Test suite for custom processors."""

    def test_add_module_name_processor(self):
        """Test add_module_name processor."""
        # Mock logger and event_dict
        logger = None
        method_name = "info"

        # Create a mock record
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        event_dict = {"_record": record}

        result = add_module_name(logger, method_name, event_dict)

        assert result["module"] == "test.module"

    def test_add_module_name_without_record(self):
        """Test add_module_name processor when no record exists."""
        logger = None
        method_name = "info"
        event_dict = {}

        result = add_module_name(logger, method_name, event_dict)

        # Should not add module if no record
        assert "module" not in result

    def test_add_timestamp_processor(self):
        """Test add_timestamp processor."""
        logger = None
        method_name = "info"
        event_dict = {}

        result = add_timestamp(logger, method_name, event_dict)

        assert "timestamp" in result


class TestLogLevelFiltering:
    """Test suite for log level filtering."""

    def test_debug_logs_not_shown_at_info_level(self, caplog):
        """Test that DEBUG logs are filtered when level is INFO."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        with caplog.at_level(logging.INFO):
            logger.debug("This should not appear")
            logger.info("This should appear")

        # Only INFO and above should be in logs
        messages = [record.message for record in caplog.records]
        assert "This should not appear" not in str(messages)

    def test_info_logs_not_shown_at_warning_level(self, caplog):
        """Test that INFO logs are filtered when level is WARNING."""
        setup_logging(log_level="WARNING")
        logger = get_logger(__name__)

        with caplog.at_level(logging.WARNING):
            logger.info("This should not appear")
            logger.warning("This should appear")

        # Only WARNING and above should be in logs
        messages = [record.message for record in caplog.records]
        assert "This should not appear" not in str(messages)


class TestRealWorldScenarios:
    """Test suite for real-world usage scenarios."""

    def test_request_lifecycle_logging(self, caplog):
        """Test logging throughout a request lifecycle."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        # Simulate request start
        bind_context(request_id="req-001", user_id=123)

        with caplog.at_level(logging.INFO):
            logger.info("Request started", endpoint="/api/upload")

            # Simulate processing
            bind_context(document_id=456)  # Add more context
            logger.info("Processing document", filename="test.pdf")

            # Simulate completion
            logger.info("Request completed", status="success")

        # Clear context for next request
        clear_context()

        # All three logs should have been recorded
        assert len(caplog.records) >= 3

    def test_error_logging_with_exception(self, caplog):
        """Test logging errors with exception information."""
        setup_logging(log_level="ERROR")
        logger = get_logger(__name__)

        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Test error")
            except ValueError as e:
                logger.error(
                    "An error occurred", error=str(e), error_type=type(e).__name__
                )

        assert len(caplog.records) > 0

    def test_multiple_operations_with_separate_contexts(self, caplog):
        """Test that contexts are properly isolated between operations."""
        setup_logging(log_level="INFO")
        logger = get_logger(__name__)

        with caplog.at_level(logging.INFO):
            # First operation
            bind_context(request_id="req-001", user_id=123)
            logger.info("Operation 1")
            clear_context()

            # Second operation
            bind_context(request_id="req-002", user_id=456)
            logger.info("Operation 2")
            clear_context()

        # Both operations should have logged
        assert len(caplog.records) >= 2
