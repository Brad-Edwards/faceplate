"""Integration tests for cascade delete behavior."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.mcp_config import MCPConfig
from app.models.message import Message
from app.models.user import User


@pytest.mark.asyncio
async def test_delete_user_cascades_to_conversations(db_session: AsyncSession) -> None:
    """Test SC-003: Delete user cascades to conversations."""
    # Create user with conversations
    user = User(email="cascade1@test.com", subject_id="cascade-sub-1")
    db_session.add(user)
    await db_session.flush()

    conv1 = Conversation(user_id=user.id, title="Conv 1")
    conv2 = Conversation(user_id=user.id, title="Conv 2")
    db_session.add_all([conv1, conv2])
    await db_session.flush()

    conv1_id, conv2_id = conv1.id, conv2.id

    # Delete user
    await db_session.delete(user)
    await db_session.flush()

    # Verify conversations are deleted
    result = await db_session.execute(select(Conversation).where(Conversation.id.in_([conv1_id, conv2_id])))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_delete_user_cascades_to_messages(db_session: AsyncSession) -> None:
    """Test SC-003: Delete user cascades through conversations to messages."""
    # Create user -> conversation -> messages
    user = User(email="cascade2@test.com", subject_id="cascade-sub-2")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Cascade Test")
    db_session.add(conv)
    await db_session.flush()

    msg1 = Message(conversation_id=conv.id, role="user", content="Hello")
    msg2 = Message(conversation_id=conv.id, role="assistant", content="Hi there")
    db_session.add_all([msg1, msg2])
    await db_session.flush()

    msg1_id, msg2_id = msg1.id, msg2.id

    # Delete user
    await db_session.delete(user)
    await db_session.flush()

    # Verify messages are deleted
    result = await db_session.execute(select(Message).where(Message.id.in_([msg1_id, msg2_id])))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_delete_conversation_cascades_to_messages(
    db_session: AsyncSession,
) -> None:
    """Test SC-003: Delete conversation cascades to messages."""
    user = User(email="cascade3@test.com", subject_id="cascade-sub-3")
    db_session.add(user)
    await db_session.flush()

    conv = Conversation(user_id=user.id, title="Will Delete")
    db_session.add(conv)
    await db_session.flush()

    msg = Message(conversation_id=conv.id, role="user", content="Bye")
    db_session.add(msg)
    await db_session.flush()

    msg_id = msg.id

    # Delete only the conversation
    await db_session.delete(conv)
    await db_session.flush()

    # Verify message is deleted
    result = await db_session.execute(select(Message).where(Message.id == msg_id))
    assert result.scalar_one_or_none() is None

    # User should still exist
    result = await db_session.execute(select(User).where(User.id == user.id))
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_delete_user_cascades_to_mcp_configs(db_session: AsyncSession) -> None:
    """Test SC-003: Delete user cascades to MCP configs."""
    user = User(email="cascade4@test.com", subject_id="cascade-sub-4")
    db_session.add(user)
    await db_session.flush()

    config = MCPConfig(
        user_id=user.id,
        name="Test MCP",
        config={"transport": "ssh"},
    )
    db_session.add(config)
    await db_session.flush()

    config_id = config.id

    # Delete user
    await db_session.delete(user)
    await db_session.flush()

    # Verify config is deleted
    result = await db_session.execute(select(MCPConfig).where(MCPConfig.id == config_id))
    assert result.scalar_one_or_none() is None
