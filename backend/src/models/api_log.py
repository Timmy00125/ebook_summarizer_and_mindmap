"""APILog model for audit trail of Gemini API calls."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, CheckConstraint, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class APILog(Base):
    """Audit trail for all Gemini API calls (debugging + cost tracking)."""

    __tablename__ = "api_logs"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key to document (nullable for metadata calls)
    document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Document being processed (NULL for metadata calls)",
    )

    # Operation details
    operation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="'summarize' or 'mindmap'",
    )

    # API metrics
    tokens_input: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Input tokens"
    )
    tokens_output: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Output tokens"
    )
    cost_usd: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 6), nullable=False, comment="Calculated cost (tokens * rate)"
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="API latency"
    )

    # Status and error tracking
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="'success', 'rate_limited', 'timeout', 'error'",
    )
    error_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="'RATE_LIMIT', 'TIMEOUT', 'AUTH_ERROR', etc.",
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Request timestamp",
    )

    # Relationships
    document: Mapped[Optional["Document"]] = relationship(
        "Document", back_populates="api_logs"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "operation IN ('summarize', 'mindmap')", name="ck_apilog_operation"
        ),
        CheckConstraint(
            "status IN ('success', 'rate_limited', 'timeout', 'error')",
            name="ck_apilog_status",
        ),
        CheckConstraint("cost_usd >= 0", name="ck_apilog_cost_positive"),
        CheckConstraint("latency_ms >= 0", name="ck_apilog_latency_positive"),
    )

    def __repr__(self) -> str:
        """String representation of APILog."""
        return (
            f"<APILog(id={self.id}, operation='{self.operation}', "
            f"status='{self.status}', cost={self.cost_usd})>"
        )
