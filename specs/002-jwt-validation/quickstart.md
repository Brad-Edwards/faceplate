# Quickstart: JWT Validation

**Feature**: 002-jwt-validation  
**Date**: 2025-12-14

## Prerequisites

- Python 3.12+
- Backend dependencies installed (`uv sync`)
- Cognito user pool configured (or mock for testing)

## Environment Variables

```bash
# Required for Cognito integration
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_APP_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Quick Validation

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Run Tests

```bash
# All JWT tests
uv run pytest tests/auth/ -v

# With coverage
uv run pytest tests/auth/ --cov=app/auth --cov-report=term-missing
```

### 3. Manual Testing

```python
from app.auth.jwt import JWTValidator
from app.core.config import get_settings

settings = get_settings()
validator = JWTValidator(settings)

# Validate a token
token = "eyJhbGciOiJS..."  # Your Cognito token
claims = await validator.validate_token(token)
print(f"Authenticated: {claims.email}")
```

## Testing Without Cognito

For local development without Cognito access:

```python
# tests/auth/conftest.py provides mock fixtures
@pytest.fixture
def mock_jwks():
    """Returns mock JWKS for testing."""
    ...

@pytest.fixture  
def valid_token(mock_jwks):
    """Returns a valid JWT signed with mock keys."""
    ...
```

## Common Issues

### "JWKS fetch failed"
- Check COGNITO_REGION and COGNITO_USER_POOL_ID
- Verify network access to AWS

### "Token signature invalid"
- Token may be from different user pool
- Check COGNITO_APP_CLIENT_ID matches token audience

### "Token expired"
- Cognito tokens expire after 1 hour
- Refresh token or get new one from Cognito

