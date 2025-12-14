# Data Model: Database Schema

**Feature**: 001-database-schema  
**Date**: 2025-12-13

## Entity Relationship Diagram

```
┌──────────────┐       ┌─────────────────┐       ┌───────────────────┐
│    users     │       │  conversations  │       │     messages      │
├──────────────┤       ├─────────────────┤       ├───────────────────┤
│ id (PK)      │──┐    │ id (PK)         │──┐    │ id (PK)           │
│ email        │  │    │ user_id (FK)    │  │    │ conversation_id   │
│ subject_id   │  └───►│ title           │  └───►│ role              │
│ created_at   │       │ created_at      │       │ content           │
└──────────────┘       │ updated_at      │       │ tool_calls        │
       │               └─────────────────┘       │ tool_results      │
       │                                         │ created_at        │
       │               ┌─────────────────┐       └───────────────────┘
       │               │   mcp_configs   │
       │               ├─────────────────┤
       └──────────────►│ id (PK)         │
                       │ user_id (FK)    │
                       │ name            │
                       │ config          │
                       │ enabled         │
                       │ created_at      │
                       │ updated_at      │
                       └─────────────────┘
```

## Entities

### users

Authenticated users from Cognito.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Primary key (uuid7) |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User email from JWT |
| subject_id | VARCHAR(255) | NOT NULL, UNIQUE | Cognito sub claim |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |

**Indexes**:
- `ix_users_email` on email
- `ix_users_subject_id` on subject_id

### conversations

Chat sessions belonging to users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Primary key (uuid7) |
| user_id | UUID | FK users.id, NOT NULL | Owner reference |
| title | VARCHAR(255) | NOT NULL, DEFAULT 'New Chat' | Conversation title |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Last update timestamp |

**Indexes**:
- `ix_conversations_user_id` on user_id

**Constraints**:
- FK user_id REFERENCES users(id) ON DELETE CASCADE

### messages

Messages within conversations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Primary key (uuid7) |
| conversation_id | UUID | FK conversations.id, NOT NULL | Conversation reference |
| role | VARCHAR(20) | NOT NULL | user, assistant, system, tool |
| content | TEXT | NULL | Message text content |
| tool_calls | JSONB | NULL | Tool call requests (assistant) |
| tool_results | JSONB | NULL | Tool call results (tool role) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |

**Indexes**:
- `ix_messages_conversation_id` on conversation_id
- `ix_messages_created_at` on created_at

**Constraints**:
- FK conversation_id REFERENCES conversations(id) ON DELETE CASCADE
- CHECK role IN ('user', 'assistant', 'system', 'tool')

### mcp_configs

Per-user MCP server configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Primary key (uuid7) |
| user_id | UUID | FK users.id, NOT NULL | Owner reference |
| name | VARCHAR(100) | NOT NULL | Server display name |
| config | JSONB | NOT NULL | Server configuration |
| enabled | BOOLEAN | NOT NULL, DEFAULT true | Whether server is active |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Last update timestamp |

**Indexes**:
- `ix_mcp_configs_user_id` on user_id
- `uq_mcp_configs_user_name` UNIQUE on (user_id, name)

**Constraints**:
- FK user_id REFERENCES users(id) ON DELETE CASCADE

## JSONB Schemas

### tool_calls (messages.tool_calls)

```json
[
  {
    "id": "call_abc123",
    "function": {
      "name": "execute_command",
      "arguments": "{\"command\": \"ls -la\"}"
    }
  }
]
```

### tool_results (messages.tool_results)

```json
[
  {
    "tool_call_id": "call_abc123",
    "content": "total 48\ndrwxr-xr-x  5 user user 4096..."
  }
]
```

### config (mcp_configs.config)

```json
{
  "transport": "ssh",
  "host": "10.1.1.10",
  "port": 22,
  "username": "kali",
  "auth": {
    "type": "key",
    "key_secret_id": "arn:aws:secretsmanager:..."
  }
}
```

## Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| users | conversations | 1:N | CASCADE |
| users | mcp_configs | 1:N | CASCADE |
| conversations | messages | 1:N | CASCADE |

## Validation Rules

| Entity | Rule |
|--------|------|
| users.email | Valid email format |
| messages.role | One of: user, assistant, system, tool |
| mcp_configs.name | Unique per user |

