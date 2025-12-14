"""Initial schema.

Revision ID: 001
Revises:
Create Date: 2025-12-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create faceplate schema and all tables."""
    # Create schema
    op.execute("CREATE SCHEMA IF NOT EXISTS faceplate")

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("subject_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("subject_id", name=op.f("uq_users_subject_id")),
        schema="faceplate",
    )
    op.create_index(
        op.f("ix_users_email"), "users", ["email"], unique=False, schema="faceplate"
    )
    op.create_index(
        op.f("ix_users_subject_id"),
        "users",
        ["subject_id"],
        unique=False,
        schema="faceplate",
    )

    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "title",
            sa.String(length=255),
            server_default="New Chat",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["faceplate.users.id"],
            name=op.f("fk_conversations_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversations")),
        schema="faceplate",
    )
    op.create_index(
        op.f("ix_conversations_user_id"),
        "conversations",
        ["user_id"],
        unique=False,
        schema="faceplate",
    )

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tool_calls", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "tool_results", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["faceplate.conversations.id"],
            name=op.f("fk_messages_conversation_id_conversations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")),
        schema="faceplate",
    )
    op.create_index(
        op.f("ix_messages_conversation_id"),
        "messages",
        ["conversation_id"],
        unique=False,
        schema="faceplate",
    )
    op.create_index(
        op.f("ix_messages_created_at"),
        "messages",
        ["created_at"],
        unique=False,
        schema="faceplate",
    )

    # Create mcp_configs table
    op.create_table(
        "mcp_configs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["faceplate.users.id"],
            name=op.f("fk_mcp_configs_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mcp_configs")),
        sa.UniqueConstraint("user_id", "name", name="uq_mcp_configs_user_id_name"),
        schema="faceplate",
    )
    op.create_index(
        op.f("ix_mcp_configs_user_id"),
        "mcp_configs",
        ["user_id"],
        unique=False,
        schema="faceplate",
    )


def downgrade() -> None:
    """Drop all tables and schema."""
    op.drop_index(
        op.f("ix_mcp_configs_user_id"), table_name="mcp_configs", schema="faceplate"
    )
    op.drop_table("mcp_configs", schema="faceplate")

    op.drop_index(
        op.f("ix_messages_created_at"), table_name="messages", schema="faceplate"
    )
    op.drop_index(
        op.f("ix_messages_conversation_id"), table_name="messages", schema="faceplate"
    )
    op.drop_table("messages", schema="faceplate")

    op.drop_index(
        op.f("ix_conversations_user_id"),
        table_name="conversations",
        schema="faceplate",
    )
    op.drop_table("conversations", schema="faceplate")

    op.drop_index(
        op.f("ix_users_subject_id"), table_name="users", schema="faceplate"
    )
    op.drop_index(op.f("ix_users_email"), table_name="users", schema="faceplate")
    op.drop_table("users", schema="faceplate")

    op.execute("DROP SCHEMA IF EXISTS faceplate")
