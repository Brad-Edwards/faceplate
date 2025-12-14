# Quickstart: Database Schema

**Feature**: 001-database-schema  
**Date**: 2025-12-13

## Prerequisites

- Docker installed (for local PostgreSQL)
- Python 3.12+
- uv package manager

## Setup

### 1. Start Local Database

```bash
cd backend
docker compose up -d postgres
```

Or use existing PostgreSQL:
```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/faceplate"
```

### 2. Install Dependencies

```bash
cd backend
uv sync --group dev
```

### 3. Run Migrations

```bash
cd backend
uv run alembic upgrade head
```

## Validation

### Test 1: Schema Created

```bash
# Connect to database
docker exec -it faceplate-postgres psql -U postgres -d faceplate

# Verify schema and tables exist
\dn faceplate
\dt faceplate.*
```

**Expected**:
```
        List of schemas
   Name    |  Owner   
-----------+----------
 faceplate | postgres

              List of relations
  Schema   |     Name      | Type  |  Owner   
-----------+---------------+-------+----------
 faceplate | users         | table | postgres
 faceplate | conversations | table | postgres
 faceplate | messages      | table | postgres
 faceplate | mcp_configs   | table | postgres
```

### Test 2: Run Unit Tests

```bash
cd backend
uv run pytest tests/models/ -v
```

**Expected**: All tests pass

### Test 3: Cascade Delete

```sql
-- In psql
INSERT INTO faceplate.users (id, email, subject_id) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'sub-123');

INSERT INTO faceplate.conversations (id, user_id, title)
VALUES ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Test Chat');

INSERT INTO faceplate.messages (id, conversation_id, role, content)
VALUES ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'user', 'Hello');

-- Delete user, verify cascade
DELETE FROM faceplate.users WHERE email = 'test@example.com';
SELECT COUNT(*) FROM faceplate.conversations; -- Should be 0
SELECT COUNT(*) FROM faceplate.messages; -- Should be 0
```

### Test 4: Connection Pool

```bash
cd backend
uv run pytest tests/db/test_pool.py -v
```

**Expected**: Pool handles 50 concurrent queries

## Success Criteria Checklist

- [ ] SC-001: Migrations complete in under 5 seconds
- [ ] SC-002: Connection pool handles 50 concurrent queries
- [ ] SC-003: Foreign key cascades work correctly

## Troubleshooting

### Migration Fails

```bash
# Check current revision
uv run alembic current

# Check history
uv run alembic history

# Downgrade and retry
uv run alembic downgrade base
uv run alembic upgrade head
```

### Connection Pool Exhausted

Check `max_connections` in PostgreSQL:
```sql
SHOW max_connections;
```

Ensure pool_size + max_overflow < max_connections.

