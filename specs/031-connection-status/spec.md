# Feature Specification: Connection Status

**Feature Branch**: `031-connection-status`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 022-frontend-shell, 023-websocket-hook

## User Scenarios & Testing

### User Story 1 - Status Indicator (Priority: P1)

User can see current connection status.

**Why this priority**: User needs to know if they're connected.

**Independent Test**: Connected shows green, disconnected shows red.

**Acceptance Scenarios**:

1. **Given** WebSocket connected, **When** displayed, **Then** indicator shows connected (green)
2. **Given** WebSocket disconnected, **When** displayed, **Then** indicator shows disconnected (red)
3. **Given** WebSocket connecting, **When** displayed, **Then** indicator shows connecting (yellow/loading)

---

### User Story 2 - Reconnection UI (Priority: P1)

User sees reconnection attempts.

**Why this priority**: User shouldn't think app is broken during reconnect.

**Independent Test**: Disconnect, verify reconnecting message shown.

**Acceptance Scenarios**:

1. **Given** reconnecting, **When** displayed, **Then** message shows "Reconnecting..."
2. **Given** reconnection succeeds, **When** connected, **Then** message clears
3. **Given** reconnection fails repeatedly, **When** displayed, **Then** retry option shown

---

### User Story 3 - Error Banner (Priority: P2)

Connection errors show banner with details.

**Why this priority**: User needs to understand connection issues.

**Independent Test**: Auth error, verify error banner shown.

**Acceptance Scenarios**:

1. **Given** connection error, **When** occurs, **Then** error banner displayed
2. **Given** error banner, **When** displayed, **Then** includes error message
3. **Given** error resolved, **When** reconnected, **Then** banner dismissed

---

### Edge Cases

- What happens when network goes offline? → Show offline indicator
- What happens when auth fails on reconnect? → Redirect to login

## Requirements

### Functional Requirements

- **FR-001**: System MUST show connection status indicator
- **FR-002**: System MUST indicate: connected, disconnected, connecting
- **FR-003**: System MUST show reconnection status
- **FR-004**: System MUST show error banner on connection errors
- **FR-005**: System MUST auto-dismiss banner on reconnection
- **FR-006**: System SHOULD provide manual reconnect option

### Key UI Components

- **ConnectionIndicator**: Status dot/icon in header
- **ReconnectionBanner**: Banner during reconnection
- **ErrorBanner**: Banner for connection errors

## Success Criteria

- **SC-001**: Status indicator reflects connection
- **SC-002**: Reconnection visible to user
- **SC-003**: Errors clearly communicated

