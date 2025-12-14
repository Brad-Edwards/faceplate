"""Tests for User model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession) -> None:
    """Test creating a new user."""
    user = User(
        email="test@example.com",
        subject_id="cognito-sub-123",
    )
    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.subject_id == "cognito-sub-123"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_user_email_unique(db_session: AsyncSession) -> None:
    """Test that email must be unique."""
    user1 = User(email="unique@example.com", subject_id="sub-1")
    user2 = User(email="unique@example.com", subject_id="sub-2")

    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(Exception, match=r"duplicate|unique"):
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_subject_id_unique(db_session: AsyncSession) -> None:
    """Test that subject_id must be unique."""
    user1 = User(email="user1@example.com", subject_id="same-sub")
    user2 = User(email="user2@example.com", subject_id="same-sub")

    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(Exception, match=r"duplicate|unique"):
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_query(db_session: AsyncSession) -> None:
    """Test querying users."""
    user = User(email="query@example.com", subject_id="query-sub")
    db_session.add(user)
    await db_session.flush()

    result = await db_session.execute(select(User).where(User.email == "query@example.com"))
    fetched = result.scalar_one()

    assert fetched.id == user.id
    assert fetched.subject_id == "query-sub"
