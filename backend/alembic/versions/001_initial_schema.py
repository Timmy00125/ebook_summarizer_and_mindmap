"""Initial schema with users, documents, summaries, mindmaps, api_logs

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables."""

    # Create enum types
    op.execute(
        "CREATE TYPE upload_status_enum AS ENUM ('uploading', 'parsing', 'ready', 'failed')"
    )
    op.execute(
        "CREATE TYPE generation_status_enum AS ENUM ('queued', 'generating', 'complete', 'failed')"
    )
    op.execute(
        "CREATE TYPE mindmap_status_enum AS ENUM ('queued', 'generating', 'complete', 'failed')"
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            comment="Email for authentication",
        ),
        sa.Column(
            "name", sa.String(length=255), nullable=False, comment="User display name"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Account creation time",
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last updated time",
        ),
        sa.Column(
            "deleted_at", sa.TIMESTAMP(), nullable=True, comment="Soft delete flag"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)

    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "filename",
            sa.String(length=255),
            nullable=False,
            comment="Original filename (e.g., 'research.pdf')",
        ),
        sa.Column(
            "file_path",
            sa.Text(),
            nullable=False,
            comment="Full path to stored file (local or S3)",
        ),
        sa.Column(
            "file_size_bytes",
            sa.Integer(),
            nullable=False,
            comment="Size for quota enforcement",
        ),
        sa.Column(
            "file_hash",
            sa.String(length=64),
            nullable=False,
            comment="SHA-256 hash for deduplication",
        ),
        sa.Column(
            "page_count",
            sa.Integer(),
            nullable=True,
            comment="Number of pages (extracted during parse)",
        ),
        sa.Column(
            "extracted_text",
            sa.Text(),
            nullable=True,
            comment="Full document text (for full-text search)",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="PDF metadata: {author, creation_date, title, subject}",
        ),
        sa.Column(
            "upload_status",
            sa.Enum(
                "uploading", "parsing", "ready", "failed", name="upload_status_enum"
            ),
            nullable=False,
            server_default="uploading",
            comment="States: uploading, parsing, ready, failed",
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Human-readable error if upload/parse fails",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Upload timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last status update",
        ),
        sa.Column(
            "expires_at",
            sa.TIMESTAMP(),
            nullable=False,
            comment="Auto-delete date (30 days from upload)",
        ),
        sa.CheckConstraint("file_size_bytes <= 104857600", name="ck_document_max_size"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "file_hash", name="uq_user_document_hash"),
    )
    op.create_index(
        op.f("ix_documents_user_id"), "documents", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_documents_created_at"), "documents", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_documents_upload_status"), "documents", ["upload_status"], unique=False
    )
    op.create_index(
        op.f("ix_documents_expires_at"), "documents", ["expires_at"], unique=False
    )
    op.create_index(
        "ix_documents_user_created",
        "documents",
        ["user_id", "created_at"],
        unique=False,
    )

    # Create summaries table
    op.create_table(
        "summaries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column(
            "summary_text",
            sa.Text(),
            nullable=False,
            comment="Summary content (formatted with bullets/paragraphs)",
        ),
        sa.Column(
            "generation_status",
            sa.Enum(
                "queued",
                "generating",
                "complete",
                "failed",
                name="generation_status_enum",
            ),
            nullable=False,
            server_default="queued",
            comment="States: queued, generating, complete, failed",
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Error detail if generation fails",
        ),
        sa.Column(
            "tokens_input",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Gemini API input tokens",
        ),
        sa.Column(
            "tokens_output",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Gemini API output tokens",
        ),
        sa.Column(
            "latency_ms",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="API call latency in milliseconds",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Generation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Status update timestamp",
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id"),
    )
    op.create_index(
        op.f("ix_summaries_document_id"), "summaries", ["document_id"], unique=True
    )
    op.create_index(
        op.f("ix_summaries_generation_status"),
        "summaries",
        ["generation_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_summaries_created_at"), "summaries", ["created_at"], unique=False
    )

    # Create mindmaps table
    op.create_table(
        "mindmaps",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column(
            "mindmap_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="Structured hierarchy: {title, children: [...]}",
        ),
        sa.Column(
            "generation_status",
            sa.Enum(
                "queued", "generating", "complete", "failed", name="mindmap_status_enum"
            ),
            nullable=False,
            server_default="queued",
            comment="States: queued, generating, complete, failed",
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Error detail if generation fails",
        ),
        sa.Column(
            "tokens_input",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Gemini API input tokens",
        ),
        sa.Column(
            "tokens_output",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Gemini API output tokens",
        ),
        sa.Column(
            "latency_ms",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="API call latency in milliseconds",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Generation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Status update timestamp",
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id"),
    )
    op.create_index(
        op.f("ix_mindmaps_document_id"), "mindmaps", ["document_id"], unique=True
    )
    op.create_index(
        op.f("ix_mindmaps_generation_status"),
        "mindmaps",
        ["generation_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mindmaps_created_at"), "mindmaps", ["created_at"], unique=False
    )

    # Create api_logs table
    op.create_table(
        "api_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "document_id",
            sa.Integer(),
            nullable=True,
            comment="Document being processed (NULL for metadata calls)",
        ),
        sa.Column(
            "operation",
            sa.String(length=50),
            nullable=False,
            comment="'summarize' or 'mindmap'",
        ),
        sa.Column("tokens_input", sa.Integer(), nullable=False, comment="Input tokens"),
        sa.Column(
            "tokens_output", sa.Integer(), nullable=False, comment="Output tokens"
        ),
        sa.Column(
            "cost_usd",
            sa.DECIMAL(precision=10, scale=6),
            nullable=False,
            comment="Calculated cost (tokens * rate)",
        ),
        sa.Column("latency_ms", sa.Integer(), nullable=False, comment="API latency"),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            comment="'success', 'rate_limited', 'timeout', 'error'",
        ),
        sa.Column(
            "error_code",
            sa.String(length=50),
            nullable=True,
            comment="'RATE_LIMIT', 'TIMEOUT', 'AUTH_ERROR', etc.",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Request timestamp",
        ),
        sa.CheckConstraint(
            "operation IN ('summarize', 'mindmap')", name="ck_apilog_operation"
        ),
        sa.CheckConstraint(
            "status IN ('success', 'rate_limited', 'timeout', 'error')",
            name="ck_apilog_status",
        ),
        sa.CheckConstraint("cost_usd >= 0", name="ck_apilog_cost_positive"),
        sa.CheckConstraint("latency_ms >= 0", name="ck_apilog_latency_positive"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_api_logs_document_id"), "api_logs", ["document_id"], unique=False
    )
    op.create_index(
        op.f("ix_api_logs_created_at"), "api_logs", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_api_logs_operation"), "api_logs", ["operation"], unique=False
    )
    op.create_index(op.f("ix_api_logs_status"), "api_logs", ["status"], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f("ix_api_logs_status"), table_name="api_logs")
    op.drop_index(op.f("ix_api_logs_operation"), table_name="api_logs")
    op.drop_index(op.f("ix_api_logs_created_at"), table_name="api_logs")
    op.drop_index(op.f("ix_api_logs_document_id"), table_name="api_logs")
    op.drop_table("api_logs")

    op.drop_index(op.f("ix_mindmaps_created_at"), table_name="mindmaps")
    op.drop_index(op.f("ix_mindmaps_generation_status"), table_name="mindmaps")
    op.drop_index(op.f("ix_mindmaps_document_id"), table_name="mindmaps")
    op.drop_table("mindmaps")

    op.drop_index(op.f("ix_summaries_created_at"), table_name="summaries")
    op.drop_index(op.f("ix_summaries_generation_status"), table_name="summaries")
    op.drop_index(op.f("ix_summaries_document_id"), table_name="summaries")
    op.drop_table("summaries")

    op.drop_index("ix_documents_user_created", table_name="documents")
    op.drop_index(op.f("ix_documents_expires_at"), table_name="documents")
    op.drop_index(op.f("ix_documents_upload_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_created_at"), table_name="documents")
    op.drop_index(op.f("ix_documents_user_id"), table_name="documents")
    op.drop_table("documents")

    op.drop_index(op.f("ix_users_created_at"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS mindmap_status_enum")
    op.execute("DROP TYPE IF EXISTS generation_status_enum")
    op.execute("DROP TYPE IF EXISTS upload_status_enum")
