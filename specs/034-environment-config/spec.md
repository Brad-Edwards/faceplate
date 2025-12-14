# Feature Specification: Environment Config

**Feature Branch**: `034-environment-config`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: None (configuration foundation)

## User Scenarios & Testing

### User Story 1 - Environment Variables (Priority: P1)

Application reads configuration from environment.

**Why this priority**: Standard configuration pattern.

**Independent Test**: Set env var, verify app uses it.

**Acceptance Scenarios**:

1. **Given** DATABASE_URL set, **When** app starts, **Then** connects to that database
2. **Given** env var not set, **When** app starts, **Then** uses default or fails clearly
3. **Given** invalid env var value, **When** app starts, **Then** validation error shown

---

### User Story 2 - Required vs Optional (Priority: P1)

Required config causes startup failure if missing.

**Why this priority**: Fail fast on misconfiguration.

**Independent Test**: Omit required var, verify startup fails.

**Acceptance Scenarios**:

1. **Given** required var missing, **When** app starts, **Then** fails with clear message
2. **Given** optional var missing, **When** app starts, **Then** uses default value
3. **Given** all required vars set, **When** app starts, **Then** starts successfully

---

### User Story 3 - Secrets from Secrets Manager (Priority: P2)

Sensitive config can come from secrets manager.

**Why this priority**: Production security.

**Independent Test**: Configure secrets manager path, verify value retrieved.

**Acceptance Scenarios**:

1. **Given** SECRET_ARN set, **When** app starts, **Then** fetches from secrets manager
2. **Given** secrets manager unavailable, **When** fetch fails, **Then** fallback to env var
3. **Given** secret fetched, **When** used, **Then** value is correct

---

### Edge Cases

- What happens when secrets manager times out? → Retry once, then fail
- What happens when env var has whitespace? → Trim whitespace

## Requirements

### Functional Requirements

- **FR-001**: System MUST read config from environment variables
- **FR-002**: System MUST validate required variables at startup
- **FR-003**: System MUST provide sensible defaults for optional vars
- **FR-004**: System SHOULD support secrets manager for sensitive values
- **FR-005**: System MUST NOT log sensitive configuration values
- **FR-006**: System MUST validate config types (int, bool, string)

### Key Config Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| COGNITO_USER_POOL_ID | Yes | - | Cognito user pool ID |
| COGNITO_REGION | No | us-east-1 | AWS region for Cognito |
| BEDROCK_ENDPOINT | Yes | - | Bedrock API endpoint |
| BEDROCK_MODEL | No | claude-3-5-sonnet | Default model |
| MAX_TOOL_CALLS | No | 20 | Max tool calls per turn |

## Success Criteria

- **SC-001**: All config read from environment
- **SC-002**: Missing required config fails fast
- **SC-003**: Secrets not logged

