# Development

Local development setup and contribution guidelines.

## Prerequisites

**Required:**
- Python 3.12+
- Node.js 22+
- Docker and Docker Compose
- PostgreSQL 16+ (or use Docker)
- AWS CLI v2
- `uv` (Python package manager)

**Optional:**
- `direnv` for environment management
- `httpie` or `curl` for API testing
- PostgreSQL client (`psql`)

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/faceplate.git
cd faceplate
```

### 2. Backend Setup

```bash
cd backend

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --group dev

# Create .env file
cp .env.example .env

# Edit .env with local values
vim .env
```

**Example `.env`:**
```bash
# Database
DATABASE_URL=postgresql://faceplate:devpass@localhost:5432/faceplate_dev

# Cognito (use dev environment values)
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxx

# Bedrock (point to local mock or dev BAG)
BEDROCK_ENDPOINT=http://localhost:8080
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# MCP
MCP_KEY_BUCKET=shifter-dev-keys
MCP_CONNECTION_TIMEOUT=30

# Agent limits
MAX_TOOL_CALLS=20
MAX_CONSECUTIVE_TOOLS=10
MESSAGE_RATE_LIMIT=100
```

### 3. Database Setup

**Using Docker:**
```bash
docker run -d \
  --name faceplate-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=faceplate \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=faceplate_dev \
  postgres:16-alpine
```

**Using local PostgreSQL:**
```bash
createdb faceplate_dev
psql faceplate_dev -c "CREATE USER faceplate WITH PASSWORD 'devpass';"
psql faceplate_dev -c "GRANT ALL PRIVILEGES ON DATABASE faceplate_dev TO faceplate;"
```

**Run migrations:**
```bash
# From backend/
psql $DATABASE_URL -f ../migrations/001_initial_schema.sql
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (if needed)
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

### 5. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Workflow

### Making Changes

**1. Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

**2. Make changes:**
- Backend: Edit files in `backend/app/`
- Frontend: Edit files in `frontend/src/`
- Migrations: Add new file to `migrations/`

**3. Test locally:**
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests (when implemented)
cd frontend
npm run test

# Linting
cd backend && uv run ruff check .
cd frontend && npm run lint
```

**4. Commit:**
```bash
git add .
git commit -m "feat: add XYZ feature"
```

**5. Push and create PR:**
```bash
git push origin feature/your-feature-name
# Create PR on GitHub
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(backend): add rate limiting for agent loop
fix(frontend): resolve WebSocket reconnection issue
docs: update deployment guide with new env vars
refactor(backend): simplify MCP manager initialization
```

## Testing

### Backend Tests

**Run all tests:**
```bash
cd backend
uv run pytest
```

**Run with coverage:**
```bash
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Run specific test:**
```bash
uv run pytest tests/test_auth.py::test_validate_valid_token
```

**Watch mode:**
```bash
uv run pytest-watch
```

### Test Structure

```python
# tests/conftest.py - Fixtures

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Conversation, Message

@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("postgresql://faceplate:devpass@localhost:5432/faceplate_test")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "email": "test@example.com",
        "sub": "123456789",
        "groups": []
    }

@pytest.fixture
def mock_range(db_session):
    """Create a test range with MCP config."""
    from app.models import MCPConfig
    
    config = MCPConfig(
        range_id="550e8400-e29b-41d4-a716-446655440000",
        config={
            "servers": [
                {
                    "name": "kali",
                    "host": "10.1.1.10",
                    "port": 22,
                    "user": "kali",
                    "key_path": "/tmp/test-key.pem"
                }
            ]
        }
    )
    db_session.add(config)
    db_session.commit()
    
    return config
```

### Frontend Tests (Future)

```typescript
// src/components/Message.test.tsx

import { render, screen } from '@testing-library/react';
import Message from './Message';

describe('Message', () => {
  it('renders user message correctly', () => {
    const message = {
      role: 'user',
      content: 'Hello, world!',
      timestamp: Date.now()
    };
    
    render(<Message message={message} />);
    
    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    expect(screen.getByText('👤')).toBeInTheDocument();
  });
  
  it('renders tool call with arguments', () => {
    const message = {
      role: 'tool',
      content: 'Executing command',
      timestamp: Date.now(),
      toolCall: {
        tool: 'kali_execute_command',
        arguments: { command: 'whoami' }
      }
    };
    
    render(<Message message={message} />);
    
    expect(screen.getByText(/kali_execute_command/)).toBeInTheDocument();
    expect(screen.getByText(/whoami/)).toBeInTheDocument();
  });
});
```

## Linting and Formatting

### Backend (Python)

**Check linting:**
```bash
cd backend
uv run ruff check .
```

**Fix auto-fixable issues:**
```bash
uv run ruff check --fix .
```

**Check formatting:**
```bash
uv run ruff format --check .
```

**Format code:**
```bash
uv run ruff format .
```

**Configuration:**
```toml
# backend/pyproject.toml

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "S", "T20", "SIM", "RUF"]
ignore = ["S101", "S105", "RUF012", "S608"]
```

### Frontend (TypeScript)

**Check linting:**
```bash
cd frontend
npm run lint
```

**Fix auto-fixable issues:**
```bash
npm run lint:fix
```

**Check formatting:**
```bash
npm run format:check
```

**Format code:**
```bash
npm run format
```

**Configuration:**
```javascript
// frontend/eslint.config.js

import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
    },
  }
);
```

## Debugging

### Backend Debugging

**VS Code launch.json:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DATABASE_URL": "postgresql://faceplate:devpass@localhost:5432/faceplate_dev"
      }
    }
  ]
}
```

**Print debugging:**
```python
# Use structlog for better debugging
import structlog
logger = structlog.get_logger()

logger.debug("Processing message", user=user_email, message_length=len(message))
```

**Interactive debugging:**
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or with iPython
import IPython; IPython.embed()
```

### Frontend Debugging

**Browser DevTools:**
- Chrome/Edge: F12 or Ctrl+Shift+I
- Firefox: F12 or Ctrl+Shift+I
- Safari: Cmd+Option+I

**React DevTools:**
Install extension:
- Chrome: [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- Firefox: [React DevTools](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

**Console logging:**
```typescript
// Structured logging
console.log('[WebSocket] Received chunk:', chunk);
console.error('[Chat] Failed to send message:', error);

// Use debugger statement
debugger;
```

## Database Management

### Migrations

**Create new migration:**
```bash
# Create migration file
vim migrations/002_add_conversation_tags.sql
```

**Example migration:**
```sql
-- migrations/002_add_conversation_tags.sql

-- Add tags column
ALTER TABLE conversations
ADD COLUMN tags TEXT[];

-- Add index on tags
CREATE INDEX idx_conversations_tags ON conversations USING GIN(tags);

-- Backfill empty tags
UPDATE conversations SET tags = '{}' WHERE tags IS NULL;
```

**Apply migrations:**
```bash
./scripts/migrate.sh
```

**Rollback migration:**
```bash
# Manually write and execute rollback
psql $DATABASE_URL -c "
  ALTER TABLE conversations DROP COLUMN tags;
  DROP INDEX idx_conversations_tags;
"
```

### Database Inspection

**Connect to database:**
```bash
psql $DATABASE_URL
```

**Common queries:**
```sql
-- List all tables
\dt

-- Describe table
\d conversations

-- Count conversations
SELECT COUNT(*) FROM conversations;

-- Recent conversations
SELECT id, user_email, title, created_at
FROM conversations
ORDER BY created_at DESC
LIMIT 10;

-- Messages per conversation
SELECT c.id, c.title, COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id
ORDER BY message_count DESC;

-- Find conversations with tool calls
SELECT DISTINCT c.id, c.title
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
WHERE m.tool_calls IS NOT NULL;
```

## Environment Management

### Using direnv

**Install direnv:**
```bash
# macOS
brew install direnv

# Linux
curl -sfL https://direnv.net/install.sh | bash

# Add to ~/.bashrc or ~/.zshrc
eval "$(direnv hook bash)"  # or zsh
```

**Create `.envrc`:**
```bash
# .envrc

export DATABASE_URL="postgresql://faceplate:devpass@localhost:5432/faceplate_dev"
export COGNITO_REGION="us-east-1"
export COGNITO_USER_POOL_ID="us-east-1_XXXXXX"
export COGNITO_CLIENT_ID="xxxxxxxxxxxx"
export BEDROCK_ENDPOINT="http://localhost:8080"
export BEDROCK_MODEL="anthropic.claude-3-5-sonnet-20241022-v2:0"
export MCP_KEY_BUCKET="shifter-dev-keys"
```

**Allow direnv:**
```bash
direnv allow
```

### Multiple Environments

**Development:**
```bash
# .env.dev
DATABASE_URL=postgresql://faceplate:devpass@localhost:5432/faceplate_dev
BEDROCK_ENDPOINT=http://localhost:8080
```

**Staging:**
```bash
# .env.staging
DATABASE_URL=postgresql://faceplate:stagingpass@staging-rds:5432/faceplate_staging
BEDROCK_ENDPOINT=https://staging-bag.example.com
```

**Load environment:**
```bash
# Backend
cd backend
cp .env.dev .env
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
cp .env.staging .env.local
npm run dev
```

## Mock Services

### Mock Bedrock (for local dev)

**Simple HTTP mock:**
```python
# scripts/mock_bedrock.py

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """Mock Bedrock chat completions."""
    return {
        "id": "mock-123",
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "choices": [{
            "delta": {"content": "This is a mock response."},
            "finish_reason": "stop"
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**Run mock:**
```bash
python scripts/mock_bedrock.py
```

### Mock MCP Server

**Echo MCP server:**
```python
# scripts/mock_mcp.py

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/tools/list")
async def list_tools():
    """List available tools."""
    return [
        {
            "name": "execute_command",
            "description": "Execute a shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    ]

@app.post("/tools/call")
async def call_tool(request: dict):
    """Execute tool (mock)."""
    tool_name = request["name"]
    arguments = request["arguments"]
    
    if tool_name == "execute_command":
        return {
            "stdout": f"Mock output for: {arguments['command']}",
            "stderr": "",
            "exit_code": 0
        }
    
    return {"error": "Unknown tool"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

## Troubleshooting

### Common Issues

**1. Database connection failed:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql $DATABASE_URL -c "SELECT 1;"

# Reset database
docker rm -f faceplate-postgres
# Then recreate (see Database Setup)
```

**2. JWT validation failing:**
```bash
# Verify Cognito pool ID
aws cognito-idp describe-user-pool \
  --user-pool-id $COGNITO_USER_POOL_ID

# Check JWT token
echo $JWT_TOKEN | cut -d. -f2 | base64 -d | jq .

# Verify public keys URL
curl https://cognito-idp.us-east-1.amazonaws.com/$COGNITO_USER_POOL_ID/.well-known/jwks.json
```

**3. WebSocket connection refused:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check WebSocket upgrade
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: localhost:8000" \
  -H "Origin: http://localhost:5173" \
  http://localhost:8000/ws/chat
```

**4. Frontend not connecting to backend:**
```bash
# Check Vite proxy config
cat frontend/vite.config.ts

# Check browser console for errors
# Open DevTools > Console

# Try direct backend API
curl http://localhost:8000/health
```

**5. MCP tool execution failing:**
```bash
# Check SSH key exists
ls -la ~/.ssh/

# Test SSH connection manually
ssh -i /path/to/key.pem kali@10.1.1.10

# Check MCP config in database
psql $DATABASE_URL -c "SELECT config FROM mcp_configs LIMIT 1;"
```

## Performance Profiling

### Backend Profiling

**Using py-spy:**
```bash
# Install
pip install py-spy

# Profile running process
py-spy record -o profile.svg --pid $(pgrep -f uvicorn)

# View in browser
open profile.svg
```

**Using cProfile:**
```python
# Add to code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... code to profile ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Frontend Profiling

**React Profiler:**
```typescript
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: string,
  actualDuration: number
) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

<Profiler id="Chat" onRender={onRenderCallback}>
  <Chat />
</Profiler>
```

**Chrome Performance Tab:**
1. Open DevTools > Performance
2. Click Record
3. Interact with app
4. Stop recording
5. Analyze flame graph

## Documentation

### Code Documentation

**Python docstrings:**
```python
def process_message(message: str, user: Dict) -> AsyncGenerator[Dict, None]:
    """Process user message and stream responses.
    
    Args:
        message: User message text
        user: Authenticated user dict with email and sub
    
    Yields:
        Response chunks (content, tool_call, tool_result, done)
    
    Raises:
        ValueError: If message is too long or invalid
        AgentError: If agent loop fails
    """
    pass
```

**TypeScript JSDoc:**
```typescript
/**
 * WebSocket hook for chat streaming.
 * 
 * @param onMessage - Callback for incoming message chunks
 * @returns Object with sendMessage function and connected status
 * 
 * @example
 * ```typescript
 * const { sendMessage, connected } = useWebSocket({
 *   onMessage: (chunk) => console.log(chunk)
 * });
 * ```
 */
export function useWebSocket({ onMessage }: UseWebSocketOptions) {
  // ...
}
```

### Updating Documentation

**When to update docs:**
- Adding new features
- Changing API endpoints
- Modifying configuration
- Updating dependencies
- Changing deployment process

**Documentation files:**
- `docs/index.md` - Overview and quick start
- `docs/architecture.md` - System design
- `docs/backend.md` - Backend implementation
- `docs/frontend.md` - Frontend implementation
- `docs/deployment.md` - Deployment procedures
- `docs/security.md` - Security controls
- `docs/development.md` - This file

## Contributing

### Pull Request Process

1. Create feature branch from `dev`
2. Make changes with tests
3. Lint and format code
4. Update documentation
5. Push and create PR
6. Wait for CI/CD checks
7. Request review
8. Address feedback
9. Merge to `dev`
10. Deploy to dev environment
11. Test in dev
12. Merge `dev` to `main` for production

### Code Review Checklist

**Reviewer should check:**
- [ ] Code follows project style guide
- [ ] Tests cover new functionality
- [ ] Documentation is updated
- [ ] No sensitive data in logs
- [ ] Error handling is appropriate
- [ ] Performance impact is acceptable
- [ ] Security considerations are addressed
- [ ] Database migrations are safe

## Resources

**Project Documentation:**
- [Architecture](architecture.md)
- [Backend](backend.md)
- [Frontend](frontend.md)
- [Deployment](deployment.md)
- [Security](security.md)

**External Resources:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

**Getting Help:**
- GitHub Issues: Report bugs and feature requests
- Team Chat: Internal Slack channel
- Documentation: Search docs/ folder

