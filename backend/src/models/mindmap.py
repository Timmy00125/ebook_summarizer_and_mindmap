"""Mindmap model for generated hierarchical mindmaps."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Mindmap(Base):
    """Generated hierarchical mindmap (JSON)."""

    __tablename__ = "mindmaps"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key to document (1:1 relationship in MVP)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Mindmap content (structured JSON)
    mindmap_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Structured hierarchy: {title, children: [...]}",
    )

    # Processing status
    generation_status: Mapped[str] = mapped_column(
        Enum("queued", "generating", "complete", "failed", name="mindmap_status_enum"),
        nullable=False,
        server_default="queued",
        index=True,
        comment="States: queued, generating, complete, failed",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Error detail if generation fails"
    )

    # API metrics (for cost tracking and monitoring)
    tokens_input: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Gemini API input tokens"
    )
    tokens_output: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Gemini API output tokens"
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="API call latency in milliseconds"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Generation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Status update timestamp",
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="mindmap")

    def __repr__(self) -> str:
        """String representation of Mindmap."""
        return (
            f"<Mindmap(id={self.id}, document_id={self.document_id}, "
            f"status='{self.generation_status}')>"
        )
