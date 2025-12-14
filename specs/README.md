# Faceplate Specifications

41 specs covering all aspects of the Faceplate agentic chat interface.

## Dependency Graph

```
Foundation (parallel):
├── 001-database-schema
├── 002-jwt-validation
├── 009-bedrock-client
├── 016-mcp-client
├── 022-frontend-shell
└── 034-environment-config

Backend Core:
003-user-management ──────────────────┐
    ↓                                 │
004-websocket-core ───────────────────┤
    ↓                                 │
005-conversation-crud                 │
    ↓                                 │
006-conversation-list                 │
    ↓                                 │
007-message-storage                   │
    ↓                                 │
008-message-roles                     │
                                      │
LLM Integration:                      │
010-streaming-response                │
    ↓                                 │
011-stream-to-websocket ──────────────┤
    ↓                                 │
012-llm-error-handling                │
                                      │
Agent Loop:                           │
013-context-builder ──────────────────┤
    ↓                                 │
014-agent-orchestrator                │
    ↓                                 │
015-agent-safety                      │
                                      │
MCP Integration:                      │
017-mcp-transport                     │
    ↓                                 │
018-mcp-user-auth                     │
    ↓                                 │
019-tool-discovery                    │
    ↓                                 │
020-tool-execution                    │
    ↓                                 │
021-tool-persistence ─────────────────┘

Frontend:
023-websocket-hook ───┐
024-auth-flow ────────┤
025-message-list ─────┤
026-message-input ────┤
027-streaming-render ─┤
028-tool-display ─────┤
029-conversation-list ┤
030-conversation-switch
031-connection-status ┘

Deployment & Testing:
032-dockerfile
033-local-dev
035-health-check
036-backend-test-setup
037-frontend-test-setup
038-integration-tests
```

## Spec Index

### Backend Foundation (001-004)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 001 | database-schema | Tables, migrations, connection pooling | P1 |
| 002 | jwt-validation | Cognito signature verification, key caching | P1 |
| 003 | user-management | User creation on first login, lookup | P1 |
| 004 | websocket-core | Connection lifecycle, auth on connect | P1 |

### Conversation & Messages (005-008)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 005 | conversation-crud | Create, read, delete conversations | P1 |
| 006 | conversation-list | List conversations, sorting, pagination | P1 |
| 007 | message-storage | Persist and retrieve messages | P1 |
| 008 | message-roles | User, assistant, tool role handling | P1 |

### LLM Integration (009-012)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 009 | bedrock-client | Bedrock API client, request formatting | P1 |
| 010 | streaming-response | Parse streaming tokens, tool calls | P1 |
| 011 | stream-to-websocket | Forward tokens to WebSocket | P1 |
| 012 | llm-error-handling | Timeouts, retries, error responses | P1 |

### Agent Loop (013-015)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 013 | context-builder | Build conversation context for LLM | P1 |
| 014 | agent-orchestrator | Main loop, tool calling, iteration | P1 |
| 015 | agent-safety | Max tools, rate limiting, abuse prevention | P1 |

### MCP Integration (016-021)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 016 | mcp-client | MCP SDK integration, connection management | P1 |
| 017 | mcp-transport | SSH and stdio transport layers | P1 |
| 018 | mcp-user-auth | Per-user MCP credentials and config | P1 |
| 019 | tool-discovery | Fetch tool definitions from MCP servers | P1 |
| 020 | tool-execution | Route and execute tool calls | P1 |
| 021 | tool-persistence | Save tool calls and results | P1 |

### Frontend Foundation (022-024)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 022 | frontend-shell | App layout, routing, theme | P1 |
| 023 | websocket-hook | WebSocket connection, reconnection | P1 |
| 024 | auth-flow | JWT from cookie, auth state | P1 |

### Frontend Chat (025-028)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 025 | message-list | Display messages, auto-scroll | P1 |
| 026 | message-input | Text input, keyboard shortcuts | P1 |
| 027 | streaming-render | Incremental token display | P1 |
| 028 | tool-display | Tool call and result rendering | P1 |

### Frontend Conversations (029-031)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 029 | conversation-list | Sidebar conversation list | P1 |
| 030 | conversation-switch | Load history on switch | P1 |
| 031 | connection-status | Status indicator, reconnection UI | P1 |

### Deployment (032-035)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 032 | dockerfile | Multi-stage Docker build | P1 |
| 033 | local-dev | Docker Compose, hot reload | P1 |
| 034 | environment-config | Env vars, secrets management | P1 |
| 035 | health-check | Health endpoint, dependency checks | P1 |

### Testing (036-038)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 036 | backend-test-setup | pytest, fixtures, coverage | P1 |
| 037 | frontend-test-setup | Vitest, React Testing Library | P1 |
| 038 | integration-tests | WebSocket, LLM, MCP integration | P1 |

### Operations (039-041)
| # | Name | Description | Priority |
|---|------|-------------|----------|
| 039 | cloudwatch-logging | Structured JSON logs to CloudWatch | P1 |
| 040 | mcp-config-management | CRUD for MCP server configs | P1 |
| 041 | tool-filtering | Disable specific tools per conversation | P1 |

## Implementation Order

### Phase 1: Foundation (can be parallel)
- 001-database-schema
- 002-jwt-validation
- 009-bedrock-client
- 016-mcp-client
- 022-frontend-shell
- 034-environment-config

### Phase 2: Backend Core
- 003-user-management
- 004-websocket-core
- 005-conversation-crud
- 007-message-storage

### Phase 3: LLM + Agent
- 010-streaming-response
- 011-stream-to-websocket
- 013-context-builder
- 014-agent-orchestrator

### Phase 4: MCP
- 017-mcp-transport
- 018-mcp-user-auth
- 019-tool-discovery
- 020-tool-execution

### Phase 5: Frontend
- 023-websocket-hook
- 024-auth-flow
- 025-message-list
- 026-message-input
- 027-streaming-render

### Phase 6: Polish
- Remaining specs (006, 008, 012, 015, 021, 028-031)
- 032-038 (deployment + testing)

## Constitution Compliance

All specs verified against constitution:

- ✅ I. Minimalism - Only required features
- ✅ II. Multi-Chat - Context isolation (005, 030)
- ✅ III. MCP-First - Per-user auth (018)
- ✅ IV. Test-First - All specs have acceptance scenarios
- ✅ V. Shared Infrastructure - PostgreSQL only (001)
- ✅ VI. Security - JWT validation (002), user isolation (003, 005)
