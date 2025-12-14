"""Async database session factory and engine configuration."""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/faceplate",
)

# Create async engine with connection pooling
# Pool configuration per spec: pool_size=5, max_overflow=15 (20 total)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=15,
    pool_timeout=30,
    pool_pre_ping=True,
)

# Async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class DatabaseConnectionError(Exception):
    """Raised when database connection fails after retries."""

    pass


@asynccontextmanager
async def get_session(
    max_retries: int = 1,
    retry_delay: float = 1.0,
) -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with retry logic.

    Args:
        max_retries: Number of retry attempts for connection errors.
        retry_delay: Delay in seconds between retries.

    Usage:
        async with get_session() as session:
            result = await session.execute(...)

    Raises:
        DatabaseConnectionError: If connection fails after all retries.
    """
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        session = async_session_factory()
        try:
            yield session
            await session.commit()
            return
        except (OperationalError, DBAPIError) as e:
            await session.rollback()
            last_error = e

            # Check if this is a connection error worth retrying
            if attempt < max_retries:
                logger.warning(
                    "Database connection error (attempt %d/%d): %s. Retrying in %ss...",
                    attempt + 1,
                    max_retries + 1,
                    str(e),
                    retry_delay,
                )
                await asyncio.sleep(retry_delay)
                continue
            else:
                logger.error(
                    "Database connection failed after %d attempts: %s",
                    max_retries + 1,
                    str(e),
                )
                raise DatabaseConnectionError(f"Database connection failed after {max_retries + 1} attempts") from e
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Should not reach here, but just in case
    if last_error:
        raise DatabaseConnectionError("Database connection failed") from last_error


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with get_session() as session:
        yield session
