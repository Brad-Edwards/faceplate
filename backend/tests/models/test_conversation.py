"""Tests for Conversation model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.user import User


@pytest.mark.asyncio
async def test_create_conversation(db_session: AsyncSession) -> None:
    """Test creating a new conversation."""
    user = User(email="conv@example.com", subject_id="conv-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(
        user_id=user.id,
        title="Test Conversation",
    )
    db_session.add(conversation)
    await db_session.flush()

    assert conversation.id is not None
    assert conversation.user_id == user.id
    assert conversation.title == "Test Conversation"
    assert conversation.created_at is not None
    assert conversation.updated_at is not None


@pytest.mark.asyncio
async def test_conversation_default_title(db_session: AsyncSession) -> None:
    """Test that conversation has default title."""
    user = User(email="default@example.com", subject_id="default-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id)
    db_session.add(conversation)
    await db_session.flush()

    assert conversation.title == "New Chat"


@pytest.mark.asyncio
async def test_conversation_user_relationship(db_session: AsyncSession) -> None:
    """Test conversation to user relationship."""
    user = User(email="rel@example.com", subject_id="rel-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id, title="Relationship Test")
    db_session.add(conversation)
    await db_session.flush()

    # Query with relationship
    result = await db_session.execute(select(Conversation).where(Conversation.user_id == user.id))
    fetched = result.scalar_one()

    assert fetched.user_id == user.id


@pytest.mark.asyncio
async def test_conversation_cascade_delete(db_session: AsyncSession) -> None:
    """Test that deleting user cascades to conversations."""
    user = User(email="cascade@example.com", subject_id="cascade-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id, title="Will be deleted")
    db_session.add(conversation)
    await db_session.flush()

    conv_id = conversation.id

    # Delete user
    await db_session.delete(user)
    await db_session.flush()

    # Conversation should be deleted
    result = await db_session.execute(select(Conversation).where(Conversation.id == conv_id))
    assert result.scalar_one_or_none() is None
