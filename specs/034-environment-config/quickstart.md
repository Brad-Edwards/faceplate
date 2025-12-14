# Quickstart: Environment Config

**Feature**: 034-environment-config  
**Date**: 2025-12-14

## Prerequisites

- Python 3.12+
- Backend dependencies installed (`uv sync`)

## Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/faceplate

# Cognito (required for auth)
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_APP_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Optional Variables

```bash
# Cognito
COGNITO_REGION=us-east-1  # default

# Bedrock
BEDROCK_ENDPOINT=http://localhost:8080  # BAG endpoint
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# Application
LOG_LEVEL=INFO
MAX_TOOL_CALLS=20
JWKS_CACHE_TTL=3600
```

## Quick Validation

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Validate Config Loads

```bash
# Set minimum required vars
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/faceplate"
export COGNITO_USER_POOL_ID="us-east-1_Test"
export COGNITO_APP_CLIENT_ID="test-client"

# Test config loads
uv run python -c "from app.core.config import get_settings; print(get_settings())"
```

### 3. Test Missing Required Var

```bash
# Unset required var
unset COGNITO_USER_POOL_ID

# Should fail with validation error
uv run python -c "from app.core.config import get_settings; get_settings()"
# Expected: pydantic_core._pydantic_core.ValidationError
```

### 4. Run Tests

```bash
uv run pytest tests/core/ -v
```

## Local Development

Create a `.env` file (not committed):

```bash
# .env (local development only)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/faceplate
COGNITO_USER_POOL_ID=us-east-1_LocalDev
COGNITO_APP_CLIENT_ID=local-dev-client
LOG_LEVEL=DEBUG
```

Load with:
```bash
export $(grep -v '^#' .env | xargs)
```

## Common Issues

### "ValidationError: field required"
- Missing a required environment variable
- Check which field is missing in the error message

### "Invalid DATABASE_URL"
- URL format must be: `postgresql+asyncpg://user:pass@host:port/db`
- Ensure `+asyncpg` driver is specified

### "Secrets Manager access denied"
- Check IAM permissions for `secretsmanager:GetSecretValue`
- Verify secret ARN is correct

