"""Tests for database migrations."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_schema_exists(db_session: AsyncSession) -> None:
    """Test that faceplate schema exists."""
    result = await db_session.execute(
        text(
            """
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name = 'faceplate'
        """
        )
    )
    schema = result.scalar_one_or_none()
    assert schema == "faceplate"


@pytest.mark.asyncio
async def test_users_table_exists(db_session: AsyncSession) -> None:
    """Test that users table exists with correct columns."""
    result = await db_session.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'faceplate' AND table_name = 'users'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}

    assert "id" in columns
    assert "email" in columns
    assert "subject_id" in columns
    assert "created_at" in columns
    assert columns["id"]["nullable"] == "NO"
    assert columns["email"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_conversations_table_exists(db_session: AsyncSession) -> None:
    """Test that conversations table exists with correct columns."""
    result = await db_session.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'faceplate' AND table_name = 'conversations'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}

    assert "id" in columns
    assert "user_id" in columns
    assert "title" in columns
    assert "created_at" in columns
    assert "updated_at" in columns


@pytest.mark.asyncio
async def test_messages_table_exists(db_session: AsyncSession) -> None:
    """Test that messages table exists with correct columns."""
    result = await db_session.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'faceplate' AND table_name = 'messages'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}

    assert "id" in columns
    assert "conversation_id" in columns
    assert "role" in columns
    assert "content" in columns
    assert "tool_calls" in columns
    assert "tool_results" in columns
    assert "created_at" in columns


@pytest.mark.asyncio
async def test_mcp_configs_table_exists(db_session: AsyncSession) -> None:
    """Test that mcp_configs table exists with correct columns."""
    result = await db_session.execute(
        text(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'faceplate' AND table_name = 'mcp_configs'
            ORDER BY ordinal_position
        """
        )
    )
    columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}

    assert "id" in columns
    assert "user_id" in columns
    assert "name" in columns
    assert "config" in columns
    assert "enabled" in columns
    assert "created_at" in columns
    assert "updated_at" in columns


@pytest.mark.asyncio
async def test_foreign_keys_exist(db_session: AsyncSession) -> None:
    """Test that foreign key constraints exist."""
    result = await db_session.execute(
        text(
            """
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'faceplate'
        """
        )
    )
    fks = [(row[1], row[2], row[3]) for row in result]

    # conversations.user_id -> users
    assert ("conversations", "user_id", "users") in fks
    # messages.conversation_id -> conversations
    assert ("messages", "conversation_id", "conversations") in fks
    # mcp_configs.user_id -> users
    assert ("mcp_configs", "user_id", "users") in fks
