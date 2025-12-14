# Backend

FastAPI application handling agent orchestration, MCP tool calling, and WebSocket streaming.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py          # Declarative base, mixins
│   │   ├── user.py          # User model
│   │   ├── conversation.py  # Conversation model
│   │   ├── message.py       # Message model
│   │   └── mcp_config.py    # MCP config model
│   └── db/
│       ├── __init__.py
│       ├── session.py       # Async session factory, pooling
│       └── migrations/      # Alembic migrations
│           ├── env.py
│           └── versions/
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── models/              # Model tests
│   └── db/                  # Database tests
├── alembic.ini
└── pyproject.toml
```

## Database Schema

All tables use the `faceplate` PostgreSQL schema.

### Users

Authenticated users from Cognito.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (uuid7) |
| email | VARCHAR(255) | Unique email from JWT |
| subject_id | VARCHAR(255) | Cognito sub claim |
| created_at | TIMESTAMPTZ | Creation timestamp |

### Conversations

Chat sessions per user.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users (CASCADE) |
| title | VARCHAR(255) | Conversation title |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update |

### Messages

Messages within conversations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | FK to conversations (CASCADE) |
| role | VARCHAR(20) | user, assistant, system, tool |
| content | TEXT | Message text |
| tool_calls | JSONB | Tool call requests |
| tool_results | JSONB | Tool execution results |
| created_at | TIMESTAMPTZ | Creation timestamp |

### MCP Configs

Per-user MCP server configurations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users (CASCADE) |
| name | VARCHAR(100) | Server display name |
| config | JSONB | Server configuration |
| enabled | BOOLEAN | Whether active |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update |

## Connection Pooling

Configured in `app/db/session.py`:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| pool_size | 5 | Base connections |
| max_overflow | 15 | Burst capacity (20 total) |
| pool_timeout | 30 | Wait time before error |
| pool_pre_ping | True | Detect stale connections |

## Migrations

Using Alembic with async support:

```bash
# Run migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Rollback one
uv run alembic downgrade -1
```

## Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-fail-under=80

# Specific tests
uv run pytest tests/models/
```

## Linting

```bash
# Check
uv run ruff check .

# Fix
uv run ruff check --fix .

# Format
uv run ruff format .
```

## Dependencies

Key production dependencies:
- FastAPI - Web framework
- SQLAlchemy 2.0 - ORM (async)
- asyncpg - PostgreSQL async driver
- Alembic - Migrations
- uuid6 - UUID7 generation

See `pyproject.toml` for full list.
