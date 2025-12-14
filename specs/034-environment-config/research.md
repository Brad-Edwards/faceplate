# Research: Environment Config

**Feature**: 034-environment-config  
**Date**: 2025-12-14

## Decision Log

### 1. Configuration Library

**Decision**: Use `pydantic-settings` (already in project)

**Rationale**:
- Already used in existing config.py
- Type validation built-in
- Environment variable parsing with nested delimiter support
- Excellent for required vs optional field distinction

**Alternatives Considered**:
- `python-dotenv`: Less type safety
- `dynaconf`: More complex than needed
- Manual os.environ: No validation

### 2. Required vs Optional Validation

**Decision**: Use Pydantic field definitions with/without defaults

**Rationale**:
- Fields without defaults are automatically required
- Pydantic raises ValidationError on missing required fields
- Clear startup failure with descriptive message

**Implementation Pattern**:
```python
class Settings(BaseSettings):
    database_url: str  # Required (no default)
    log_level: str = "INFO"  # Optional (has default)
```

### 3. Secrets Manager Integration

**Decision**: Optional boto3 integration with fallback to env vars

**Rationale**:
- Production needs Secrets Manager for sensitive values
- Development uses plain env vars
- Graceful fallback maintains local dev experience

**Pattern**:
- Check for `*_SECRET_ARN` env var
- If present, fetch from Secrets Manager
- If not, use direct `*` env var

### 4. Sensitive Value Logging

**Decision**: Use `SecretStr` type from Pydantic

**Rationale**:
- Automatically redacts value in repr/str
- Prevents accidental logging
- Still accessible via `.get_secret_value()`

**Example**:
```python
from pydantic import SecretStr

class Settings(BaseSettings):
    database_url: SecretStr  # Won't appear in logs
```

### 5. Environment Variable Naming

**Decision**: SCREAMING_SNAKE_CASE with logical grouping

**Rationale**:
- Standard convention for env vars
- Nested settings use `__` delimiter (e.g., `COGNITO__REGION`)
- Pydantic handles conversion to snake_case attributes

## Configuration Variables

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| DATABASE_URL | Yes | - | Yes | PostgreSQL connection string |
| COGNITO_REGION | No | us-east-1 | No | AWS region |
| COGNITO_USER_POOL_ID | Yes | - | No | Cognito pool ID |
| COGNITO_APP_CLIENT_ID | Yes | - | No | Cognito client ID |
| BEDROCK_ENDPOINT | No | - | No | Bedrock API endpoint (BAG URL) |
| BEDROCK_MODEL | No | anthropic.claude-3-5-sonnet-20241022-v2:0 | No | Default model ID |
| MAX_TOOL_CALLS | No | 20 | No | Max tool calls per turn |
| LOG_LEVEL | No | INFO | No | Logging level |
| JWKS_CACHE_TTL | No | 3600 | No | JWKS cache TTL in seconds |

## Open Questions

None. All technical decisions resolved.

