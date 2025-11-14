"""Structured logging utility with JSON format and context tracking.

This module provides a structured logging system using structlog for better
debugging and monitoring. Supports JSON-formatted output, context tracking
(request_id, user_id, document_id), and configurable log levels.

Example usage:
    from src.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Processing document", document_id=123, user_id=456)
    logger.error("Failed to parse PDF", error="Invalid format", request_id="abc-123")
"""

import logging
import os
import sys
from typing import Any, Optional

import structlog
from structlog.types import EventDict, Processor


def add_module_name(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add module name to log event.

    Args:
        logger: The logger instance
        method_name: Name of the logging method (info, error, etc.)
        event_dict: The event dictionary to modify

    Returns:
        Modified event dictionary with module name
    """
    record = event_dict.get("_record")
    if record:
        event_dict["module"] = record.name
    return event_dict


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO 8601 timestamp to log event.

    Args:
        logger: The logger instance
        method_name: Name of the logging method
        event_dict: The event dictionary to modify

    Returns:
        Modified event dictionary with timestamp
    """
    event_dict["timestamp"] = structlog.processors.TimeStamper(fmt="iso")(
        logger, method_name, event_dict
    )["timestamp"]
    return event_dict


def setup_logging(
    log_level: Optional[str] = None, log_format: Optional[str] = None
) -> None:
    """Configure structured logging for the application.

    This function sets up structlog with JSON formatting (or console formatting
    for development) and configures the standard library logging to work with it.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   Defaults to LOG_LEVEL env var or INFO.
        log_format: Output format ('json' or 'console'). Defaults to LOG_FORMAT
                    env var or 'json'.

    Example:
        setup_logging(log_level="DEBUG", log_format="console")
    """
    # Get configuration from environment or use defaults
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_format = log_format or os.getenv("LOG_FORMAT", "json")

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Build processor pipeline
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        add_module_name,
        add_timestamp,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate renderer based on format
    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Console format for development
        processors.append(structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty()))

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Name for the logger, typically __name__ of the module

    Returns:
        A configured structlog BoundLogger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Starting process", process_id=123)
    """
    return structlog.get_logger(name)


def bind_context(
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    document_id: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Bind context variables that will be included in all subsequent logs.

    This is useful for adding request-scoped context like request_id, user_id,
    or document_id that should appear in all logs for a particular operation.

    Args:
        request_id: Unique request identifier
        user_id: User ID performing the operation
        document_id: Document ID being processed
        **kwargs: Additional context key-value pairs

    Example:
        bind_context(request_id="abc-123", user_id=456, document_id=789)
        logger.info("Processing started")  # Will include all context
    """
    context = {}
    if request_id is not None:
        context["request_id"] = request_id
    if user_id is not None:
        context["user_id"] = user_id
    if document_id is not None:
        context["document_id"] = document_id
    context.update(kwargs)

    if context:
        structlog.contextvars.bind_contextvars(**context)


def clear_context() -> None:
    """Clear all bound context variables.

    Useful at the end of a request to ensure context doesn't leak into
    subsequent requests.

    Example:
        try:
            bind_context(request_id="abc-123")
            # ... process request ...
        finally:
            clear_context()
    """
    structlog.contextvars.clear_contextvars()


def unbind_context(*keys: str) -> None:
    """Remove specific context variables.

    Args:
        *keys: Variable names to unbind

    Example:
        unbind_context("document_id", "user_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)
