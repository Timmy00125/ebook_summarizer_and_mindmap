"""Pytest configuration and fixtures for backend tests."""


import pytest


@pytest.fixture
def sample_error_details():
    """Sample error details for testing."""
    return {
        "filename": "test.pdf",
        "size": 150000000,
        "limit": 100000000,
    }


@pytest.fixture
def sample_retry_config():
    """Sample retry configuration for testing."""
    return {
        "max_retries": 3,
        "initial_delay": 0.1,
        "max_delay": 60.0,
        "exponential_base": 2.0,
    }
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
