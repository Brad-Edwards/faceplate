# Feature Specification: Database Schema

**Feature Branch**: `001-database-schema`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: None (foundation)

## User Scenarios & Testing

### User Story 1 - Schema Initialization (Priority: P1)

Database tables exist and are ready for application use.

**Why this priority**: Nothing works without the database schema.

**Independent Test**: Run migrations, verify all tables exist with correct columns.

**Acceptance Scenarios**:

1. **Given** empty database, **When** migrations run, **Then** all required tables are created
2. **Given** existing database with data, **When** new migration runs, **Then** data is preserved and schema updated
3. **Given** migration fails midway, **When** error occurs, **Then** transaction rolls back cleanly

---

### User Story 2 - Connection Pooling (Priority: P1)

Application maintains efficient database connections.

**Why this priority**: Required for concurrent WebSocket connections.

**Independent Test**: 50 concurrent connections don't exhaust pool or create new connections per request.

**Acceptance Scenarios**:

1. **Given** application starts, **When** first query runs, **Then** connection pool is initialized
2. **Given** connection pool at capacity, **When** new request arrives, **Then** request waits for available connection (not rejected)
3. **Given** connection is stale, **When** query attempted, **Then** connection is refreshed automatically

---

### Edge Cases

- What happens when database is unreachable at startup? → Fail fast with clear error within 5 seconds
- What happens when connection drops mid-query? → Retry once with 1 second delay, then propagate error
- What happens when pool is exhausted for >30s? → Timeout with error (pool_timeout=30)

## Requirements

### Functional Requirements

- **FR-001**: System MUST create users table (id, email, subject_id, created_at)
- **FR-002**: System MUST create conversations table (id, user_id, title, created_at, updated_at)
- **FR-003**: System MUST create messages table (id, conversation_id, role, content, tool_calls, tool_results, created_at)
- **FR-004**: System MUST create mcp_configs table (id, user_id, name, config, enabled, created_at, updated_at)
- **FR-005**: System MUST use connection pooling (min 5, max 20 connections)
- **FR-006**: System MUST use UUID primary keys
- **FR-007**: System MUST enforce foreign key constraints with cascade delete
- **FR-008**: System MUST use Alembic for schema migrations
- **FR-009**: System MUST use schema `faceplate` (per constitution)

### Schema Migrations

Use Alembic for versioned migrations:
- Initial migration creates all tables
- Future changes via `alembic revision --autogenerate`
- Migrations run on app startup (or via CLI)

### Key Entities

- **users**: Authenticated users
- **conversations**: Chat sessions per user
- **messages**: Messages within conversations
- **mcp_configs**: Per-user MCP configuration

## Success Criteria

- **SC-001**: Migrations complete in under 5 seconds
- **SC-002**: Connection pool handles 50 concurrent queries
- **SC-003**: Foreign key cascades work correctly (delete conversation → delete messages)

