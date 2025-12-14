"""Tests for Message model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User


@pytest.mark.asyncio
async def test_create_message(db_session: AsyncSession) -> None:
    """Test creating a new message."""
    user = User(email="msg@example.com", subject_id="msg-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id, title="Message Test")
    db_session.add(conversation)
    await db_session.flush()

    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello, world!",
    )
    db_session.add(message)
    await db_session.flush()

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "Hello, world!"
    assert message.created_at is not None


@pytest.mark.asyncio
async def test_message_roles(db_session: AsyncSession) -> None:
    """Test message with different roles."""
    user = User(email="roles@example.com", subject_id="roles-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id)
    db_session.add(conversation)
    await db_session.flush()

    roles = ["user", "assistant", "system", "tool"]
    for role in roles:
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=f"Message from {role}",
        )
        db_session.add(message)

    await db_session.flush()

    result = await db_session.execute(select(Message).where(Message.conversation_id == conversation.id))
    messages = result.scalars().all()

    assert len(messages) == 4
    assert {m.role for m in messages} == {"user", "assistant", "system", "tool"}


@pytest.mark.asyncio
async def test_message_tool_calls(db_session: AsyncSession) -> None:
    """Test message with tool_calls JSONB field."""
    user = User(email="tools@example.com", subject_id="tools-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id)
    db_session.add(conversation)
    await db_session.flush()

    tool_calls = [
        {
            "id": "call_abc123",
            "function": {
                "name": "execute_command",
                "arguments": '{"command": "ls -la"}',
            },
        }
    ]

    message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=None,
        tool_calls=tool_calls,
    )
    db_session.add(message)
    await db_session.flush()

    result = await db_session.execute(select(Message).where(Message.id == message.id))
    fetched = result.scalar_one()

    assert fetched.tool_calls == tool_calls
    assert fetched.tool_calls[0]["function"]["name"] == "execute_command"


@pytest.mark.asyncio
async def test_message_tool_results(db_session: AsyncSession) -> None:
    """Test message with tool_results JSONB field."""
    user = User(email="results@example.com", subject_id="results-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id)
    db_session.add(conversation)
    await db_session.flush()

    tool_results = [
        {
            "tool_call_id": "call_abc123",
            "content": "total 48\ndrwxr-xr-x  5 user user 4096...",
        }
    ]

    message = Message(
        conversation_id=conversation.id,
        role="tool",
        content=None,
        tool_results=tool_results,
    )
    db_session.add(message)
    await db_session.flush()

    result = await db_session.execute(select(Message).where(Message.id == message.id))
    fetched = result.scalar_one()

    assert fetched.tool_results == tool_results


@pytest.mark.asyncio
async def test_message_cascade_delete(db_session: AsyncSession) -> None:
    """Test that deleting conversation cascades to messages."""
    user = User(email="msgcascade@example.com", subject_id="msgcascade-sub")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id)
    db_session.add(conversation)
    await db_session.flush()

    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Will be deleted",
    )
    db_session.add(message)
    await db_session.flush()

    msg_id = message.id

    # Delete conversation
    await db_session.delete(conversation)
    await db_session.flush()

    # Message should be deleted
    result = await db_session.execute(select(Message).where(Message.id == msg_id))
    assert result.scalar_one_or_none() is None
