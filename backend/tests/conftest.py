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
