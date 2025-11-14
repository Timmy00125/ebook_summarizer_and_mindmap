"""Middleware components for the FastAPI application.

This package contains HTTP middleware for cross-cutting concerns:
- CORS configuration for frontend-backend communication
- Error handling and exception transformation
- Request/response logging and monitoring
"""

from .cors_middleware import setup_cors
from .error_middleware import setup_error_handlers

__all__ = ["setup_cors", "setup_error_handlers"]
