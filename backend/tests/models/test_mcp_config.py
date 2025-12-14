"""Tests for MCPConfig model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mcp_config import MCPConfig
from app.models.user import User


@pytest.mark.asyncio
async def test_create_mcp_config(db_session: AsyncSession) -> None:
    """Test creating a new MCP config."""
    user = User(email="mcp@example.com", subject_id="mcp-sub")
    db_session.add(user)
    await db_session.flush()

    config = {
        "transport": "ssh",
        "host": "10.1.1.10",
        "port": 22,
        "username": "kali",
    }

    mcp_config = MCPConfig(
        user_id=user.id,
        name="Kali MCP",
        config=config,
    )
    db_session.add(mcp_config)
    await db_session.flush()

    assert mcp_config.id is not None
    assert mcp_config.user_id == user.id
    assert mcp_config.name == "Kali MCP"
    assert mcp_config.config == config
    assert mcp_config.enabled is True
    assert mcp_config.created_at is not None
    assert mcp_config.updated_at is not None


@pytest.mark.asyncio
async def test_mcp_config_disabled(db_session: AsyncSession) -> None:
    """Test creating disabled MCP config."""
    user = User(email="disabled@example.com", subject_id="disabled-sub")
    db_session.add(user)
    await db_session.flush()

    mcp_config = MCPConfig(
        user_id=user.id,
        name="Disabled MCP",
        config={"transport": "stdio"},
        enabled=False,
    )
    db_session.add(mcp_config)
    await db_session.flush()

    assert mcp_config.enabled is False


@pytest.mark.asyncio
async def test_mcp_config_unique_name_per_user(db_session: AsyncSession) -> None:
    """Test that MCP config name must be unique per user."""
    user = User(email="unique@example.com", subject_id="unique-sub")
    db_session.add(user)
    await db_session.flush()

    config1 = MCPConfig(
        user_id=user.id,
        name="Same Name",
        config={"transport": "ssh"},
    )
    config2 = MCPConfig(
        user_id=user.id,
        name="Same Name",
        config={"transport": "stdio"},
    )

    db_session.add(config1)
    await db_session.flush()

    db_session.add(config2)
    with pytest.raises(Exception, match=r"duplicate|unique"):
        await db_session.flush()


@pytest.mark.asyncio
async def test_mcp_config_same_name_different_users(db_session: AsyncSession) -> None:
    """Test that different users can have same config name."""
    user1 = User(email="user1@example.com", subject_id="sub-1")
    user2 = User(email="user2@example.com", subject_id="sub-2")
    db_session.add_all([user1, user2])
    await db_session.flush()

    config1 = MCPConfig(
        user_id=user1.id,
        name="Kali",
        config={"transport": "ssh"},
    )
    config2 = MCPConfig(
        user_id=user2.id,
        name="Kali",
        config={"transport": "ssh"},
    )

    db_session.add_all([config1, config2])
    await db_session.flush()

    # Both should exist
    result = await db_session.execute(select(MCPConfig).where(MCPConfig.name == "Kali"))
    configs = result.scalars().all()
    assert len(configs) == 2


@pytest.mark.asyncio
async def test_mcp_config_cascade_delete(db_session: AsyncSession) -> None:
    """Test that deleting user cascades to MCP configs."""
    user = User(email="mcpcascade@example.com", subject_id="mcpcascade-sub")
    db_session.add(user)
    await db_session.flush()

    mcp_config = MCPConfig(
        user_id=user.id,
        name="Will be deleted",
        config={"transport": "stdio"},
    )
    db_session.add(mcp_config)
    await db_session.flush()

    config_id = mcp_config.id

    # Delete user
    await db_session.delete(user)
    await db_session.flush()

    # Config should be deleted
    result = await db_session.execute(select(MCPConfig).where(MCPConfig.id == config_id))
    assert result.scalar_one_or_none() is None
