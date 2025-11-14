"""User model for account management."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class User(Base):
    """User entity for multi-user support (extensible)."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # User credentials and profile
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email for authentication",
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="User display name"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), comment="Account creation time"
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last updated time",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="Soft delete flag"
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
