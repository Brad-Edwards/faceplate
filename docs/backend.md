# Backend

FastAPI application handling agent orchestration, MCP tool calling, and WebSocket streaming.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, routes, WebSocket
│   ├── config.py            # Settings, environment variables
│   ├── auth.py              # Cognito JWT validation
│   ├── agent.py             # Agent loop, tool calling
│   ├── mcp_manager.py       # MCP server management
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # DB connection, session management
│   └── schemas.py           # Pydantic models for API
├── tests/
│   ├── test_auth.py
│   ├── test_agent.py
│   ├── test_mcp.py
│   └── test_websocket.py
├── Dockerfile
├── requirements.txt
├── pyproject.toml           # Ruff config, pytest config
└── .env.example
```

## Core Modules

### main.py - FastAPI Application

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from app.auth import get_current_user
from app.agent import AgentOrchestrator
from app.database import get_db

app = FastAPI(title="Faceplate", version="0.1.0")

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.get("/health")
async def health_check():
    """ALB health check endpoint."""
    return {"status": "healthy"}

@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """WebSocket endpoint for chat streaming."""
    await websocket.accept()
    
    orchestrator = AgentOrchestrator(user=user, db=db)
    
    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_json()
            
            # Stream response chunks
            async for chunk in orchestrator.process_message(data["message"]):
                await websocket.send_json(chunk)
                
    except WebSocketDisconnect:
        await orchestrator.cleanup()
```

**Key Features:**
- WebSocket for streaming responses
- JWT validation via dependency injection
- Static file serving for frontend
- Async/await for concurrent connections

### config.py - Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Cognito
    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str
    cognito_client_id: str
    
    # Bedrock
    bedrock_endpoint: str
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    # MCP
    mcp_key_bucket: str
    mcp_connection_timeout: int = 30
    
    # Agent
    max_tool_calls: int = 20
    max_consecutive_tools: int = 10
    message_rate_limit: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Environment Variables:**
- Loaded from `.env` file or environment
- Validation via Pydantic
- Type-safe access throughout app

### auth.py - Authentication

```python
import jwt
from fastapi import HTTPException, WebSocket
from typing import Dict
from app.config import settings
import httpx

class CognitoJWTValidator:
    def __init__(self):
        self.jwks_client = None
        self._public_keys = None
    
    async def get_public_keys(self):
        """Fetch Cognito public keys (cached)."""
        if self._public_keys:
            return self._public_keys
            
        url = f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/"
        url += f"{settings.cognito_user_pool_id}/.well-known/jwks.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            self._public_keys = response.json()
        
        return self._public_keys
    
    async def validate_token(self, token: str) -> Dict:
        """Validate JWT and return claims."""
        try:
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            
            # Get public key
            public_keys = await self.get_public_keys()
            key = next(
                k for k in public_keys["keys"] 
                if k["kid"] == unverified_header["kid"]
            )
            
            # Verify signature and claims
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=settings.cognito_client_id,
                issuer=f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"
            )
            
            return claims
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

validator = CognitoJWTValidator()

async def get_current_user(websocket: WebSocket) -> Dict:
    """Extract and validate JWT from WebSocket."""
    # Get token from Authorization header
    auth_header = websocket.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=4001, reason="Missing or invalid token")
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.split(" ")[1]
    claims = await validator.validate_token(token)
    
    return {
        "email": claims["email"],
        "sub": claims["sub"],
        "groups": claims.get("cognito:groups", [])
    }
```

**Security:**
- JWT signature validation against Cognito public keys
- Public keys cached (refresh every hour)
- WebSocket authentication on connect
- Claims extracted for authorization

### models.py - Database Models

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String(255), nullable=False)
    range_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_user_range", "user_email", "range_id"),
    )

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSONB)
    tool_results = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index("idx_conversation", "conversation_id", "created_at"),
        CheckConstraint("role IN ('user', 'assistant', 'tool')", name="check_role"),
    )

class MCPConfig(Base):
    __tablename__ = "mcp_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    range_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    config = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Schema Design:**
- UUIDs for all primary keys
- JSONB for flexible MCP config storage
- Cascade delete on conversation → messages
- Indexes on common query patterns

### database.py - Connection Management

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Connection Pooling:**
- 10 persistent connections
- Up to 20 overflow connections
- Pre-ping to handle stale connections
- Automatic connection recycling

### mcp_manager.py - MCP Integration

```python
import asyncio
import json
from typing import Dict, List, Any
import httpx
from app.config import settings
from app.database import get_db
from app.models import MCPConfig

class MCPManager:
    def __init__(self, range_id: str, db):
        self.range_id = range_id
        self.db = db
        self.servers = {}
        self._load_config()
    
    def _load_config(self):
        """Load MCP config from database."""
        config = self.db.query(MCPConfig).filter(
            MCPConfig.range_id == self.range_id
        ).first()
        
        if not config:
            raise ValueError(f"No MCP config found for range {self.range_id}")
        
        self.config = config.config
        self._init_servers()
    
    def _init_servers(self):
        """Initialize MCP server connections."""
        for server in self.config["servers"]:
            self.servers[server["name"]] = {
                "host": server["host"],
                "port": server["port"],
                "user": server["user"],
                "key_path": server["key_path"],
                "transport": server["transport"]
            }
    
    async def list_tools(self) -> List[Dict]:
        """Get all available tools from MCP servers."""
        tools = []
        
        for server_name, server_config in self.servers.items():
            # Call MCP server to list tools
            server_tools = await self._call_mcp(
                server_name,
                "tools/list",
                {}
            )
            
            # Add server prefix to tool names
            for tool in server_tools:
                tool["name"] = f"{server_name}_{tool['name']}"
                tool["mcp_server"] = server_name
                tools.append(tool)
        
        return tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool on the appropriate MCP server."""
        # Extract server name from tool name
        server_name, actual_tool = tool_name.split("_", 1)
        
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")
        
        result = await self._call_mcp(
            server_name,
            f"tools/call",
            {
                "name": actual_tool,
                "arguments": arguments
            }
        )
        
        return result
    
    async def _call_mcp(self, server_name: str, method: str, params: Dict) -> Any:
        """Make MCP JSON-RPC call over SSH transport."""
        server = self.servers[server_name]
        
        # For MVP: Execute via SSH command wrapper
        # Future: Use native MCP Python SDK
        command = f"mcp-server {method} '{json.dumps(params)}'"
        
        result = await self._ssh_execute(
            host=server["host"],
            user=server["user"],
            key_path=server["key_path"],
            command=command
        )
        
        return json.loads(result)
    
    async def _ssh_execute(self, host: str, user: str, key_path: str, command: str) -> str:
        """Execute command over SSH."""
        # Use asyncssh library for async SSH
        import asyncssh
        
        async with asyncssh.connect(
            host,
            username=user,
            client_keys=[key_path],
            known_hosts=None  # Trust on first use (range VPC is isolated)
        ) as conn:
            result = await conn.run(command, timeout=settings.mcp_connection_timeout)
            return result.stdout
    
    async def cleanup(self):
        """Close all MCP connections."""
        # Clean up any persistent connections
        pass
```

**MCP Integration:**
- Per-range MCP configuration
- Tool discovery from MCP servers
- Tool execution over SSH transport
- Async connection management

### agent.py - Agent Orchestration

```python
from typing import AsyncGenerator, Dict, List
import httpx
from app.config import settings
from app.mcp_manager import MCPManager
from app.models import Conversation, Message
from app.database import get_db

class AgentOrchestrator:
    def __init__(self, user: Dict, db):
        self.user = user
        self.db = db
        self.mcp_manager = None
        self.conversation = None
        self.tool_call_count = 0
        self.consecutive_tool_count = 0
    
    async def process_message(self, message: str) -> AsyncGenerator[Dict, None]:
        """Process user message and stream responses."""
        # Load or create conversation
        await self._load_conversation()
        
        # Save user message
        self._save_message("user", message)
        
        # Initialize MCP manager if not already
        if not self.mcp_manager:
            self.mcp_manager = MCPManager(
                range_id=self.conversation.range_id,
                db=self.db
            )
        
        # Get available tools
        tools = await self.mcp_manager.list_tools()
        
        # Build context
        context = await self._build_context()
        
        # Agent loop
        async for chunk in self._agent_loop(context, tools):
            yield chunk
    
    async def _agent_loop(self, context: List[Dict], tools: List[Dict]) -> AsyncGenerator[Dict, None]:
        """Main agent loop with tool calling."""
        assistant_message = ""
        
        while self.tool_call_count < settings.max_tool_calls:
            # Call Bedrock
            async for response in self._call_bedrock(context, tools):
                if response["type"] == "content":
                    # Stream text to frontend
                    assistant_message += response["text"]
                    yield {
                        "type": "content",
                        "text": response["text"]
                    }
                
                elif response["type"] == "tool_call":
                    # Execute tool
                    yield {
                        "type": "tool_call",
                        "tool": response["name"],
                        "arguments": response["arguments"]
                    }
                    
                    result = await self.mcp_manager.execute_tool(
                        response["name"],
                        response["arguments"]
                    )
                    
                    yield {
                        "type": "tool_result",
                        "tool": response["name"],
                        "result": result
                    }
                    
                    # Add tool result to context
                    context.append({
                        "role": "tool",
                        "tool_call_id": response["id"],
                        "content": str(result)
                    })
                    
                    self.tool_call_count += 1
                    self.consecutive_tool_count += 1
                    
                    # Safety: Break if too many consecutive tools
                    if self.consecutive_tool_count >= settings.max_consecutive_tools:
                        yield {
                            "type": "error",
                            "message": "Too many consecutive tool calls"
                        }
                        break
                    
                    # Continue agent loop
                    break
                
                elif response["type"] == "done":
                    # Save assistant message
                    self._save_message("assistant", assistant_message)
                    
                    yield {
                        "type": "done"
                    }
                    return
    
    async def _call_bedrock(self, context: List[Dict], tools: List[Dict]) -> AsyncGenerator[Dict, None]:
        """Call Bedrock with streaming."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.bedrock_endpoint}/v1/chat/completions",
                json={
                    "model": settings.bedrock_model,
                    "messages": context,
                    "tools": tools,
                    "stream": True
                },
                timeout=60.0
            )
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    
                    if "choices" in data:
                        choice = data["choices"][0]
                        
                        if "delta" in choice:
                            delta = choice["delta"]
                            
                            if "content" in delta:
                                yield {
                                    "type": "content",
                                    "text": delta["content"]
                                }
                            
                            if "tool_calls" in delta:
                                for tool_call in delta["tool_calls"]:
                                    yield {
                                        "type": "tool_call",
                                        "id": tool_call["id"],
                                        "name": tool_call["function"]["name"],
                                        "arguments": json.loads(tool_call["function"]["arguments"])
                                    }
                        
                        if choice.get("finish_reason") == "stop":
                            yield {"type": "done"}
    
    async def _build_context(self) -> List[Dict]:
        """Build conversation context for LLM."""
        messages = self.db.query(Message).filter(
            Message.conversation_id == self.conversation.id
        ).order_by(Message.created_at).all()
        
        context = []
        for msg in messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add system prompt
        context.insert(0, {
            "role": "system",
            "content": self._get_system_prompt()
        })
        
        return context
    
    def _get_system_prompt(self) -> str:
        """System prompt for cyber range agent."""
        return """You are an AI assistant controlling a cyber range environment.

You have access to two machines via tools:
- kali: An attack machine with penetration testing tools
- victim: A target machine for security testing

Users will ask you to configure vulnerabilities, run attacks, or investigate systems.
Use the available tools to accomplish tasks. Be methodical and explain your actions.

When executing attacks, follow standard methodology:
1. Reconnaissance
2. Scanning and enumeration
3. Exploitation
4. Post-exploitation

Always confirm destructive actions before executing."""
    
    def _save_message(self, role: str, content: str):
        """Save message to database."""
        message = Message(
            conversation_id=self.conversation.id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
    
    async def _load_conversation(self):
        """Load or create conversation."""
        # For MVP: Use active range for user
        # Future: Allow conversation selection
        
        from app.models import Conversation
        
        conversation = self.db.query(Conversation).filter(
            Conversation.user_email == self.user["email"]
        ).order_by(Conversation.updated_at.desc()).first()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                user_email=self.user["email"],
                range_id=await self._get_user_active_range(),
                title="New Chat"
            )
            self.db.add(conversation)
            self.db.commit()
        
        self.conversation = conversation
    
    async def _get_user_active_range(self) -> str:
        """Get user's active range ID from Portal database."""
        # Query ranges table (from Portal schema)
        result = self.db.execute(
            "SELECT id FROM ranges WHERE user_email = :email AND status = 'active' LIMIT 1",
            {"email": self.user["email"]}
        )
        row = result.fetchone()
        
        if not row:
            raise ValueError("No active range found for user")
        
        return row[0]
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.mcp_manager:
            await self.mcp_manager.cleanup()
```

**Agent Features:**
- Streaming responses via WebSocket
- Tool calling with MCP integration
- Safety limits on tool usage
- Conversation context management
- System prompt for cyber range domain

## API Endpoints

### WebSocket: `/ws/chat`

**Connection:**
```javascript
const ws = new WebSocket("wss://shifter.example.com/ws/chat", {
  headers: {
    "Authorization": `Bearer ${jwt_token}`
  }
});
```

**Send Message:**
```json
{
  "message": "Scan the victim machine for open ports"
}
```

**Receive Chunks:**
```json
{"type": "content", "text": "I'll scan "}
{"type": "content", "text": "the victim"}
{"type": "tool_call", "tool": "kali_execute_command", "arguments": {"command": "nmap -p- 10.1.1.20"}}
{"type": "tool_result", "tool": "kali_execute_command", "result": "PORT    STATE SERVICE\n22/tcp  open  ssh\n80/tcp  open  http"}
{"type": "content", "text": "The scan shows..."}
{"type": "done"}
```

### GET `/health`

Health check for ALB.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

## Testing

### Test Structure

```python
# tests/test_auth.py
import pytest
from app.auth import CognitoJWTValidator

@pytest.mark.asyncio
async def test_validate_valid_token():
    validator = CognitoJWTValidator()
    claims = await validator.validate_token(VALID_JWT)
    assert claims["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_validate_expired_token():
    validator = CognitoJWTValidator()
    with pytest.raises(HTTPException) as exc_info:
        await validator.validate_token(EXPIRED_JWT)
    assert exc_info.value.status_code == 401

# tests/test_agent.py
import pytest
from app.agent import AgentOrchestrator

@pytest.mark.asyncio
async def test_process_message_with_tool_call(db_session, mock_mcp):
    orchestrator = AgentOrchestrator(
        user={"email": "test@example.com"},
        db=db_session
    )
    
    chunks = []
    async for chunk in orchestrator.process_message("Run nmap"):
        chunks.append(chunk)
    
    assert any(c["type"] == "tool_call" for c in chunks)
    assert any(c["type"] == "tool_result" for c in chunks)

# tests/test_mcp.py
import pytest
from app.mcp_manager import MCPManager

@pytest.mark.asyncio
async def test_list_tools(db_session, mock_range):
    manager = MCPManager(range_id=mock_range.id, db=db_session)
    tools = await manager.list_tools()
    
    assert len(tools) > 0
    assert "kali_execute_command" in [t["name"] for t in tools]

@pytest.mark.asyncio
async def test_execute_tool(db_session, mock_range):
    manager = MCPManager(range_id=mock_range.id, db=db_session)
    result = await manager.execute_tool(
        "kali_execute_command",
        {"command": "whoami"}
    )
    
    assert "kali" in result
```

### Running Tests

```bash
# Install dev dependencies
uv sync --group dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run specific test
uv run pytest tests/test_auth.py::test_validate_valid_token

# Watch mode
uv run pytest-watch
```

## Linting and Formatting

### Ruff Configuration

Already configured in `pyproject.toml` (matches Shifter Portal):

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "S", "T20", "SIM", "RUF"]
ignore = ["S101", "S105", "RUF012", "S608"]
```

### Commands

```bash
# Check linting
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Check formatting
uv run ruff format --check .

# Format code
uv run ruff format .
```

## Dependencies

### Production (`requirements.txt`)

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-jose[cryptography]==3.3.0
httpx==0.27.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
asyncssh==2.18.0
python-dotenv==1.0.1
```

### Development (`pyproject.toml` dev group)

```toml
[dependency-groups]
dev = [
    "pytest==9.0.2",
    "pytest-asyncio==0.25.2",
    "pytest-cov==7.0.0",
    "ruff==0.14.9",
    "httpx-mock==0.1.0"
]
```

## Deployment

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application
COPY app/ ./app/
COPY frontend/dist/ ./frontend/dist/

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/faceplate

# Cognito
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxx

# Bedrock
BEDROCK_ENDPOINT=http://bedrock-gateway:80
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# MCP
MCP_KEY_BUCKET=shifter-ssh-keys-prod
```

## Performance Considerations

### Connection Pooling

- SQLAlchemy pool: 10 base + 20 overflow
- HTTP client reuse for Bedrock calls
- SSH connection pooling for MCP (future)

### Caching

- Cognito public keys: Cached for 1 hour
- MCP tool definitions: Cached per range session
- No caching of chat history (always fresh from DB)

### Limits

- Max 100 concurrent WebSocket connections per instance
- Max 20 tool calls per conversation turn
- Max 10 consecutive tool calls without user input
- 30s timeout per MCP tool execution
- 60s timeout for Bedrock API calls

