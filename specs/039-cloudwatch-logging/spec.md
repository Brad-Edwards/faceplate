# Feature Specification: CloudWatch Logging

**Feature Branch**: `039-cloudwatch-logging`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 034-environment-config

## User Scenarios & Testing

### User Story 1 - Application Logs to CloudWatch (Priority: P1)

All application logs are sent to CloudWatch.

**Why this priority**: Required for production debugging.

**Independent Test**: Log message, verify appears in CloudWatch.

**Acceptance Scenarios**:

1. **Given** app running in AWS, **When** log written, **Then** appears in CloudWatch log group
2. **Given** log group configured, **When** app starts, **Then** logs to configured group
3. **Given** log written, **When** viewed, **Then** includes timestamp, level, message

---

### User Story 2 - Structured Logging (Priority: P1)

Logs are structured JSON for querying.

**Why this priority**: Need to search and filter logs.

**Independent Test**: Log entry, verify JSON format.

**Acceptance Scenarios**:

1. **Given** log entry, **When** written, **Then** formatted as JSON
2. **Given** JSON log, **When** queried, **Then** fields searchable (level, user_id, etc.)
3. **Given** request context, **When** logged, **Then** request_id included

---

### User Story 3 - Log Levels (Priority: P1)

Different log levels for different verbosity.

**Why this priority**: Control log volume.

**Independent Test**: Set level to WARNING, verify DEBUG not logged.

**Acceptance Scenarios**:

1. **Given** log level INFO, **When** DEBUG logged, **Then** not sent to CloudWatch
2. **Given** log level configurable, **When** env var set, **Then** level respected
3. **Given** ERROR logged, **When** any level, **Then** always sent

---

### User Story 4 - Request Context (Priority: P2)

Logs include request/user context.

**Why this priority**: Trace issues to specific users/requests.

**Independent Test**: Log during request, verify user_id present.

**Acceptance Scenarios**:

1. **Given** authenticated request, **When** log written, **Then** user_id included
2. **Given** request, **When** log written, **Then** request_id included
3. **Given** WebSocket, **When** log written, **Then** connection_id included

---

### Edge Cases

- What happens when CloudWatch unavailable? → Buffer locally, retry
- What happens with very high log volume? → Async logging, batch writes

## Requirements

### Functional Requirements

- **FR-001**: System MUST log to CloudWatch in production
- **FR-002**: System MUST use structured JSON format
- **FR-003**: System MUST support configurable log level
- **FR-004**: System MUST include timestamp in all logs
- **FR-005**: System MUST include request context (user_id, request_id)
- **FR-006**: System MUST NOT log sensitive data (tokens, passwords, PII)
- **FR-007**: System SHOULD batch log writes for performance

### Log Format

```json
{
  "timestamp": "2025-12-13T12:00:00Z",
  "level": "INFO",
  "message": "User sent message",
  "user_id": "abc123",
  "request_id": "req-456",
  "conversation_id": "conv-789",
  "extra": {}
}
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| LOG_LEVEL | INFO | Minimum log level |
| LOG_GROUP | /faceplate/{env} | CloudWatch log group |
| LOG_FORMAT | json | json or text (text for local dev) |

## Success Criteria

- **SC-001**: Logs appear in CloudWatch
- **SC-002**: JSON format searchable
- **SC-003**: Sensitive data not logged

