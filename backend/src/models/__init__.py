"""SQLAlchemy base model and session configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Create the declarative base for all models
Base = declarative_base()

# Import all models to ensure they're registered with Base
# This is required for Alembic to detect them
from .api_log import APILog
from .document import Document
from .mindmap import Mindmap
from .summary import Summary
from .user import User

# Database engine and session will be configured in main.py or config.py
# This is just the base setup that models will inherit from

__all__ = ["Base", "User", "Document", "Summary", "Mindmap", "APILog"]
