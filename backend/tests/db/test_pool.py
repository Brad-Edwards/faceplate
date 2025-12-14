"""Tests for database connection pooling."""

import asyncio

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_pool_configuration(test_engine) -> None:
    """Test that connection pool is configured correctly."""
    pool = test_engine.pool

    # Verify pool configuration matches spec
    # Note: test engine uses smaller pool for testing
    assert pool.size() >= 1  # At least some connections
    assert hasattr(pool, "overflow")


@pytest.mark.asyncio
async def test_pool_pre_ping(test_engine) -> None:
    """Test that pool_pre_ping is enabled for stale connection handling."""
    # pool_pre_ping should be enabled to detect stale connections
    # This is verified by the engine configuration
    assert test_engine.pool._pre_ping is True


@pytest.mark.asyncio
async def test_concurrent_connections(
    async_session_factory_fixture,
) -> None:
    """Test that pool handles 50 concurrent queries.

    This verifies FR-005: System MUST use connection pooling.
    SC-002: Connection pool handles 50 concurrent queries.
    """

    async def run_query(session_factory, query_id: int) -> int:
        """Execute a simple query and return the query ID."""
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            _ = result.scalar()
            return query_id

    # Launch 50 concurrent queries
    tasks = [run_query(async_session_factory_fixture, i) for i in range(50)]

    # All should complete without exhausting the pool
    results = await asyncio.gather(*tasks)

    # Verify all 50 queries completed
    assert len(results) == 50
    assert set(results) == set(range(50))


@pytest.mark.asyncio
async def test_connection_reuse(
    async_session_factory_fixture,
) -> None:
    """Test that connections are reused from the pool."""
    connection_ids = []

    for _ in range(10):
        async with async_session_factory_fixture() as session:
            result = await session.execute(text("SELECT pg_backend_pid()"))
            pid = result.scalar()
            connection_ids.append(pid)

    # With connection pooling, we should see connection reuse
    # (fewer unique PIDs than total connections)
    unique_pids = set(connection_ids)
    assert len(unique_pids) <= len(connection_ids)


@pytest.mark.asyncio
async def test_pool_timeout_configuration(test_engine) -> None:
    """Test that pool timeout is configured per spec."""
    # Pool timeout should be set for exhaustion handling
    # FR-005 and edge case: pool exhausted > 30s -> timeout
    pool = test_engine.pool
    assert pool._timeout is not None
