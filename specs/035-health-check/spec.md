# Feature Specification: Health Check

**Feature Branch**: `035-health-check`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 001-database-schema

## User Scenarios & Testing

### User Story 1 - Health Endpoint (Priority: P1)

Application exposes health check endpoint.

**Why this priority**: Required for load balancer and monitoring.

**Independent Test**: GET /health, verify 200 response.

**Acceptance Scenarios**:

1. **Given** app running, **When** GET /health, **Then** returns 200 OK
2. **Given** response, **When** parsed, **Then** includes status: healthy
3. **Given** app starting, **When** GET /health before ready, **Then** returns 503

---

### User Story 2 - Dependency Checks (Priority: P1)

Health check verifies critical dependencies.

**Why this priority**: Detect unhealthy state.

**Independent Test**: Database down, verify health returns unhealthy.

**Acceptance Scenarios**:

1. **Given** database connected, **When** health checked, **Then** reports healthy
2. **Given** database unreachable, **When** health checked, **Then** reports unhealthy
3. **Given** unhealthy dependency, **When** response, **Then** includes which dependency failed

---

### User Story 3 - ALB Integration (Priority: P1)

Health check works with AWS ALB.

**Why this priority**: Production deployment requirement.

**Independent Test**: ALB health check settings match endpoint behavior.

**Acceptance Scenarios**:

1. **Given** ALB configured, **When** health check runs, **Then** instance marked healthy
2. **Given** app fails health, **When** ALB checks, **Then** instance marked unhealthy
3. **Given** health response, **When** returned, **Then** completes within ALB timeout

---

### User Story 4 - Graceful Shutdown (Priority: P1)

Application shuts down gracefully on termination signal.

**Why this priority**: Don't drop connections during deploy.

**Independent Test**: Send SIGTERM, verify connections drained before exit.

**Acceptance Scenarios**:

1. **Given** SIGTERM received, **When** shutting down, **Then** health returns 503 immediately
2. **Given** shutdown started, **When** active connections exist, **Then** wait for completion (max 30s)
3. **Given** shutdown timeout reached, **When** connections still active, **Then** force close and exit

---

### Edge Cases

- What happens when health check times out? → ALB marks unhealthy
- What happens during graceful shutdown? → Health returns unhealthy immediately
- What happens when shutdown takes too long? → Force exit after timeout

## Requirements

### Functional Requirements

- **FR-001**: System MUST expose GET /health endpoint
- **FR-002**: System MUST return 200 for healthy, 503 for unhealthy
- **FR-003**: System MUST check database connectivity
- **FR-004**: System MUST complete health check within 5 seconds
- **FR-005**: System MUST include version in health response
- **FR-006**: System MUST return unhealthy during shutdown
- **FR-007**: System MUST handle SIGTERM for graceful shutdown
- **FR-008**: System MUST drain connections before exiting (max 30s)
- **FR-009**: System MUST stop accepting new connections on shutdown start

### Response Format

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "bedrock": "ok"
  }
}
```

## Success Criteria

- **SC-001**: Health endpoint returns correct status
- **SC-002**: Dependency failures detected
- **SC-003**: Response within timeout

