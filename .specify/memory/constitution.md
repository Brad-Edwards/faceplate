# Faceplate Constitution

## Core Principles

### I. Minimalism (NON-NEGOTIABLE)
- Faceplate replaces OpenWebUI because OWUI is bloated
- No features unless explicitly required for cyber range chat
- No document upload, RAG, image gen, or plugins

### II. Multi-Chat with Context Isolation
- Users can have multiple conversations
- Each conversation has isolated context
- Agent in one conversation cannot see other conversation histories

### III. MCP-First Design
- Tool calling via MCP is the core value proposition
- All tools routed through MCP manager
- Support MCP per-user authentication

### IV. Test-First (NON-NEGOTIABLE)
- TDD mandatory: Tests written → Fail → Implement → Pass
- Backend coverage ≥80% (pytest)
- All API endpoints have Pydantic schema validation

### V. Shared Infrastructure
- Same VPC, RDS, Cognito as Shifter Portal
- PostgreSQL (schema: `faceplate`)
- No Redis, no new databases

### VI. Security by Default
- JWT validation on every WebSocket connect
- Users only access their own conversations
- MCP config determines available tools (Faceplate trusts the config it receives)

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy, Python 3.12 |
| Frontend | React 18, TypeScript, Vite |
| Database | PostgreSQL 16 (shared with Portal) |
| Auth | Cognito JWT |
| LLM | Bedrock via BAG |
| Tools | MCP over SSH |

## Quality Gates

- Python: Ruff (120 char, rules: E,W,F,I,B,C4,UP,S,T20,SIM,RUF)
- TypeScript: ESLint + Prettier
- Commits: Conventional format

## Governance

Constitution supersedes all other practices. Amendments require:
1. Documentation of change reason
2. Validation against existing specs

**Version**: 1.0 | **Ratified**: 2025-12-13
