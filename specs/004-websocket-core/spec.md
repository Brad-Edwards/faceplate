# Feature Specification: WebSocket Core

**Feature Branch**: `004-websocket-core`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 002-jwt-validation, 003-user-management

## User Scenarios & Testing

### User Story 1 - Authenticated Connection (Priority: P1)

Only authenticated users can establish WebSocket connections.

**Why this priority**: Security - no anonymous access allowed.

**Independent Test**: Connection with valid JWT succeeds, without JWT fails.

**Technical Note**: WebSocket does not support custom headers in browser. JWT MUST be passed via query parameter: `ws://host/ws?token=<jwt>`. The token is validated during the HTTP upgrade before the WebSocket handshake completes.

**Acceptance Scenarios**:

1. **Given** valid JWT in `token` query parameter, **When** connection attempted, **Then** WebSocket is established
2. **Given** no token query parameter, **When** connection attempted, **Then** connection is rejected with 401
3. **Given** invalid JWT in query parameter, **When** connection attempted, **Then** connection is rejected with 401
4. **Given** expired JWT in query parameter, **When** connection attempted, **Then** connection is rejected with 401

---

### User Story 2 - Connection Lifecycle (Priority: P1)

System properly manages connection open, message, and close events.

**Why this priority**: Core WebSocket functionality.

**Independent Test**: Connect, send message, receive response, disconnect cleanly.

**Acceptance Scenarios**:

1. **Given** authenticated user, **When** connection opens, **Then** user context is established for session
2. **Given** open connection, **When** message received, **Then** message is routed to handler
3. **Given** open connection, **When** client disconnects, **Then** resources are cleaned up

---

### User Story 3 - Connection Tracking (Priority: P2)

System knows which users are currently connected.

**Why this priority**: Useful for monitoring and debugging.

**Independent Test**: Connect two users, verify both tracked, disconnect one, verify removed.

**Acceptance Scenarios**:

1. **Given** user connects, **When** connection established, **Then** connection is tracked
2. **Given** user disconnects, **When** connection closed, **Then** connection is removed from tracking

---

### Edge Cases

- What happens when user opens multiple connections? → Allow multiple, each tracked separately
- What happens when connection drops without close frame? → Detect via heartbeat, clean up
- What happens when auth token expires mid-connection? → Keep connection (validated at connect only)

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept JWT via `token` query parameter (not header)
- **FR-002**: System MUST validate JWT on WebSocket upgrade (before handshake completes)
- **FR-003**: System MUST reject connections without valid JWT (HTTP 401/403)
- **FR-004**: System MUST associate user identity (from JWT) with connection
- **FR-005**: System MUST handle graceful disconnect (cleanup resources)
- **FR-006**: System MUST handle unexpected disconnect (cleanup resources)
- **FR-007**: System MUST support multiple connections per user
- **FR-008**: System MUST configure CORS to allow WebSocket from frontend origin

### Key Entities

- **WebSocketConnection**: Active connection with user context
- **ConnectionManager**: Tracks active connections

## Success Criteria

- **SC-001**: Connection establishment under 500ms
- **SC-002**: No resource leaks after disconnect (verified by test)
- **SC-003**: 100% of connections authenticated

