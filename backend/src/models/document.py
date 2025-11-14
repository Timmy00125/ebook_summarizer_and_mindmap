"""Document model for PDF metadata and processing status."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Document(Base):
    """PDF document metadata and processing status."""

    __tablename__ = "documents"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key to user
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # File information
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Original filename (e.g., 'research.pdf')"
    )
    file_path: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Full path to stored file (local or S3)"
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Size for quota enforcement"
    )
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="SHA-256 hash for deduplication"
    )

    # Parsed document data
    page_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of pages (extracted during parse)"
    )
    extracted_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Full document text (for full-text search)"
    )
    pdf_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata",  # Column name in database
        JSONB,
        nullable=True,
        comment="PDF metadata: {author, creation_date, title, subject}",
    )

    # Processing status
    upload_status: Mapped[str] = mapped_column(
        Enum("uploading", "parsing", "ready", "failed", name="upload_status_enum"),
        nullable=False,
        server_default="uploading",
        index=True,
        comment="States: uploading, parsing, ready, failed",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Human-readable error if upload/parse fails"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Upload timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last status update",
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(days=30),
        index=True,
        comment="Auto-delete date (30 days from upload)",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    summary: Mapped[Optional["Summary"]] = relationship(
        "Summary",
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )
    mindmap: Mapped[Optional["Mindmap"]] = relationship(
        "Mindmap",
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )
    api_logs: Mapped[list["APILog"]] = relationship(
        "APILog", back_populates="document", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint("user_id", "file_hash", name="uq_user_document_hash"),
        CheckConstraint(
            "file_size_bytes <= 104857600", name="ck_document_max_size"
        ),  # 100 MB
        Index("ix_documents_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of Document."""
        return (
            f"<Document(id={self.id}, filename='{self.filename}', "
            f"status='{self.upload_status}')>"
        )
