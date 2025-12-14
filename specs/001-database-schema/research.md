# Research: Database Schema

**Feature**: 001-database-schema  
**Date**: 2025-12-13

## SQLAlchemy 2.0 Async Patterns

**Decision**: Use SQLAlchemy 2.0 with async support via asyncpg

**Rationale**:
- SQLAlchemy 2.0 has native async support
- asyncpg is the fastest PostgreSQL async driver
- Matches FastAPI's async model
- Already in project dependencies

**Alternatives Considered**:
- SQLAlchemy 1.4 sync: Rejected - would require thread pool, adds complexity
- Raw asyncpg: Rejected - loses ORM benefits, more boilerplate
- Tortoise ORM: Rejected - less mature, smaller ecosystem

**Key Patterns**:
```python
# Async session factory
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=5,
    max_overflow=15,  # Total 20 connections
    pool_pre_ping=True,  # Handle stale connections
)
```

## Alembic Async Migrations

**Decision**: Use Alembic with async engine support

**Rationale**:
- Standard migration tool for SQLAlchemy
- Supports async engines in Alembic 1.7+
- Autogenerate from models works with async

**Key Configuration**:
```python
# alembic/env.py
from sqlalchemy.ext.asyncio import async_engine_from_config

def run_migrations_online():
    connectable = async_engine_from_config(...)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
```

## UUID Primary Keys

**Decision**: Use PostgreSQL native UUID type with uuid7 generation

**Rationale**:
- UUID7 is time-ordered (better index performance than UUID4)
- Native PostgreSQL UUID type is efficient
- Avoids auto-increment conflicts in distributed scenarios

**Implementation**:
```python
from uuid import uuid7
from sqlalchemy import UUID

class Base:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )
```

**Note**: Python 3.12 doesn't have uuid7 in stdlib yet. Use `uuid6` package or generate manually.

## Connection Pool Configuration

**Decision**: Pool size 5, max overflow 15 (20 total)

**Rationale**:
- Spec requires 50 concurrent connections support
- 20 connections can handle 50 concurrent requests (connections are reused)
- Shared RDS - don't exhaust connection limit
- pool_pre_ping handles stale connections

**Configuration**:
| Parameter | Value | Reason |
|-----------|-------|--------|
| pool_size | 5 | Base connections |
| max_overflow | 15 | Burst capacity |
| pool_timeout | 30 | Wait time before error |
| pool_pre_ping | True | Detect stale connections |

## PostgreSQL Schema Isolation

**Decision**: Use `faceplate` schema within shared RDS

**Rationale**:
- Constitution mandates shared RDS with Portal
- Schema isolation prevents table name conflicts
- Each app has own schema (shifter, faceplate)

**Implementation**:
```python
# In models
__table_args__ = {"schema": "faceplate"}

# In migrations
op.execute("CREATE SCHEMA IF NOT EXISTS faceplate")
```

## JSONB for Flexible Data

**Decision**: Use JSONB for tool_calls, tool_results, mcp config

**Rationale**:
- MCP tool calls have variable structure
- JSONB allows indexing if needed later
- More efficient than JSON type

**Fields using JSONB**:
- `messages.tool_calls` - Array of tool call objects
- `messages.tool_results` - Array of tool result objects
- `mcp_configs.config` - MCP server configuration

## Cascade Delete Strategy

**Decision**: CASCADE delete for parent-child relationships

**Rationale**:
- User deleted → conversations deleted → messages deleted
- Simplifies cleanup, prevents orphans
- Spec explicitly requires this behavior

**Relationships**:
```
users (1) → (N) conversations (1) → (N) messages
users (1) → (N) mcp_configs
```

## Summary

All research items resolved. No NEEDS CLARIFICATION remaining.

| Topic | Decision |
|-------|----------|
| ORM | SQLAlchemy 2.0 async |
| Driver | asyncpg |
| Migrations | Alembic with async |
| IDs | UUID (uuid7 pattern) |
| Pool | 5 base, 15 overflow |
| Schema | `faceplate` |
| JSON fields | JSONB |
| Deletes | CASCADE |

