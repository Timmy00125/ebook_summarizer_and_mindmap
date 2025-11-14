"""API route modules for the backend.

This package contains all API endpoint routers:
- health: Service health and status checks
- documents: PDF upload and document management (TODO: T042-T045)
- summaries: AI-powered summary generation (TODO: T068-T070)
- mindmaps: Hierarchical mindmap generation (TODO: T090-T092)
"""

# Import routers for convenience
from . import health  # noqa: F401

__all__ = ["health"]
