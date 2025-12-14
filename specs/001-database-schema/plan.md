# Implementation Plan: Database Schema

**Branch**: `001-database-schema` | **Date**: 2025-12-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-database-schema/spec.md`

## Summary

Implement the foundational database schema for Faceplate using SQLAlchemy models and Alembic migrations. Creates four core tables (users, conversations, messages, mcp_configs) in the `faceplate` PostgreSQL schema with proper relationships, constraints, and connection pooling.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: SQLAlchemy 2.0, Alembic, asyncpg  
**Storage**: PostgreSQL 16 (shared RDS, schema: `faceplate`)  
**Testing**: pytest, pytest-asyncio  
**Target Platform**: Linux server (Docker/EC2)  
**Project Type**: Web application (backend)  
**Performance Goals**: 50 concurrent connections, migrations < 5 seconds  
**Constraints**: Shared RDS with Shifter Portal, no new databases  
**Scale/Scope**: MVP, multi-user chat application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Minimalism | PASS | Only core tables, no extras |
| II. Multi-Chat with Context Isolation | PASS | Conversations table supports multiple chats |
| III. MCP-First Design | PASS | mcp_configs table for per-user MCP config |
| IV. Test-First | PASS | Tests required before implementation |
| V. Shared Infrastructure | PASS | Uses shared RDS, faceplate schema |
| VI. Security by Default | N/A | Database layer, auth handled by JWT spec |

**Gate Result**: PASS - No violations

## Project Structure

### Documentation (this feature)

```text
specs/001-database-schema/
├── plan.md              # This file
├── research.md          # Phase 0: Dependency research
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Validation steps
├── contracts/           # Phase 1: N/A for database spec
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # SQLAlchemy base, mixins
│   │   ├── user.py           # User model
│   │   ├── conversation.py   # Conversation model
│   │   ├── message.py        # Message model
│   │   └── mcp_config.py     # MCP config model
│   └── db/
│       ├── __init__.py
│       ├── session.py        # Async session factory, pool config
│       └── migrations/       # Alembic migrations
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
│               └── 001_initial_schema.py
├── alembic.ini
├── tests/
│   ├── conftest.py           # DB fixtures
│   └── models/
│       ├── test_user.py
│       ├── test_conversation.py
│       ├── test_message.py
│       └── test_mcp_config.py
└── pyproject.toml
```

**Structure Decision**: Web application structure. Database models in `backend/app/models/`, migrations in `backend/app/db/migrations/`.

## Complexity Tracking

No violations - no complexity justification needed.
