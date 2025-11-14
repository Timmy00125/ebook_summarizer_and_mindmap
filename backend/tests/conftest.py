"""Test configuration and shared fixtures for pytest."""

import pytest


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration between tests to avoid state leakage."""
    yield
    # Cleanup happens after each test
    import logging
    import structlog

    # Clear structlog context
    structlog.contextvars.clear_contextvars()

    # Reset structlog configuration
    structlog.reset_defaults()

    # Clear all handlers from root logger
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
