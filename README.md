# Faceplate

Lightweight agentic chat interface for Shifter cyber range.

```
 _____ _    ____ _____ ____  _        _  _____ _____ 
|  ___/ \  / ___| ____|  _ \| |      / \|_   _| ____|
| |_ / _ \| |   |  _| | |_) | |     / _ \ | | |  _|  
|  _/ ___ \ |___| |___|  __/| |___ / ___ \| | | |___ 
|_|/_/   \_\____|_____|_|   |_____/_/   \_\_| |_____|
```

**Purpose-built chat UI for AI-controlled cyber ranges.** Replace OpenWebUI with a minimal, MCP-first design that does one thing well: connect users to Bedrock models with direct tool access to Kali and victim machines.

## Quick Start

**Prerequisites:** Python 3.12+, Node.js 22+, Docker, PostgreSQL 16+

```bash
# Clone and setup
git clone https://github.com/your-org/faceplate.git
cd faceplate

# Backend
cd backend
uv sync --group dev
cp .env.example .env
# Edit .env with your values

# Database
docker run -d --name faceplate-postgres -p 5432:5432 \
  -e POSTGRES_USER=faceplate -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=faceplate_dev postgres:16-alpine

psql postgresql://faceplate:devpass@localhost:5432/faceplate_dev \
  -f ../migrations/001_initial_schema.sql

# Start backend
uv run uvicorn app.main:app --reload

# Frontend (new terminal)
cd ../frontend
npm install
npm run dev

# Access at http://localhost:5173
```

## What is Faceplate?

Faceplate provides a chat interface where users authenticate via Cognito, select their active cyber range, and interact with AI agents that have tool access to Kali (attack) and victim (target) machines via MCP.

**Key Features:**
- Single Sign-On (AWS Cognito)
- Real-time streaming (WebSocket)
- MCP tool calling for Kali/Victim control
- Chat history persistence (PostgreSQL)
- Model selection (multiple Bedrock models)
- Range-aware (auto-loads user's active range)

**Non-Features (intentionally excluded):**
- Document upload / RAG
- Image generation
- Multiple conversations
- Plugins / extensions
- Admin interface
- Custom model endpoints

## Architecture

```
User Browser
    ↓
  React UI (WebSocket)
    ↓
FastAPI Backend (Agent Loop)
    ↓
┌──────────────┬──────────────┬─────────────┐
│ AWS Bedrock  │ MCPs (SSH)   │ PostgreSQL  │
│ - LLM calls  │ - Kali/Victim│ - Chat hist │
└──────────────┴──────────────┴─────────────┘
```

**Components:**
- **Frontend:** React + Vite, WebSocket client, message rendering
- **Backend:** FastAPI, agent orchestration, MCP management, auth
- **Database:** PostgreSQL (conversations, messages, MCP configs)
- **Auth:** AWS Cognito JWT validation
- **LLM:** AWS Bedrock via Bedrock Access Gateway
- **Tools:** MCP servers over SSH to range instances

## Documentation

| Document | Description |
|----------|-------------|
| [Overview](docs/index.md) | High-level introduction and use cases |
| [Architecture](docs/architecture.md) | System design, data flow, components |
| [Backend](docs/backend.md) | FastAPI implementation, agent loop, MCP |
| [Frontend](docs/frontend.md) | React UI, WebSocket, components |
| [Deployment](docs/deployment.md) | Docker, Terraform, CI/CD pipeline |
| [Security](docs/security.md) | Threat model, auth, encryption, auditing |
| [Development](docs/development.md) | Local setup, testing, contributing |

## Technology Stack

**Backend:**
- Python 3.12
- FastAPI (web framework)
- SQLAlchemy (ORM)
- asyncssh (MCP over SSH)
- python-jose (JWT validation)

**Frontend:**
- TypeScript 5.6
- React 18
- Vite 6 (build tool)
- Native WebSocket API

**Infrastructure:**
- Docker (containerization)
- PostgreSQL 16 (database)
- AWS EC2 (compute)
- AWS ALB (load balancing)
- AWS Cognito (authentication)
- AWS Bedrock (LLM)

## Development

### Run Locally

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Run Tests

```bash
# Backend
cd backend
uv run pytest --cov

# Frontend
cd frontend
npm run test  # (when implemented)
```

### Lint and Format

```bash
# Backend
cd backend
uv run ruff check .
uv run ruff format .

# Frontend
cd frontend
npm run lint
npm run format
```

## Deployment

### Docker Build

```bash
docker build -t faceplate:latest .
```

### Deploy to EC2

Faceplate deploys via Terraform in the Shifter Portal VPC:

```bash
cd terraform/environments/dev/faceplate
terraform init
terraform plan
terraform apply
```

See [Deployment Guide](docs/deployment.md) for full details.

## Security

**Authentication:**
- Cognito JWT validation on every WebSocket connection
- No password storage (handled by Cognito)
- Token expiration enforced

**Authorization:**
- Users can only access their own conversations
- Range access validated before MCP execution
- Tool calls scoped to user's active range

**Network:**
- Faceplate in private subnet (no direct internet)
- TLS 1.3 for all external traffic
- SSH keys encrypted in Secrets Manager

**Data Protection:**
- RDS encryption at rest
- TLS in transit for all connections
- No PII in application logs

See [Security Guide](docs/security.md) for full threat model.

## Roadmap

### MVP (Week 1-2)
- [x] Backend: FastAPI with WebSocket streaming
- [x] Frontend: React chat UI
- [x] Auth: Cognito JWT validation
- [x] Database: PostgreSQL schema
- [x] MCP: Basic tool calling
- [x] Deployment: Docker + Terraform
- [x] Documentation: Complete

### Post-MVP
- [ ] Frontend tests (Vitest)
- [ ] Rate limiting (per-user, per-hour)
- [ ] Conversation management UI (list, delete, rename)
- [ ] Model selection UI (currently hardcoded)
- [ ] MCP connection pooling (performance)
- [ ] Horizontal scaling (multi-EC2)
- [ ] Advanced agent reasoning (ReAct, ToT)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Lint and format code
5. Update documentation
6. Commit changes (`git commit -m 'feat: add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Create Pull Request

See [Development Guide](docs/development.md) for detailed instructions.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built for [Shifter](../shifter) - Agentic cyber range platform
- Inspired by OpenWebUI, but lighter and purpose-built
- Uses [Model Context Protocol](https://modelcontextprotocol.io/) for tool calling
- Powered by AWS Bedrock (Claude Sonnet 4.5)

---

**Status:** MVP in development (Week 1-2)

**Contact:** See GitHub issues for questions and bug reports

