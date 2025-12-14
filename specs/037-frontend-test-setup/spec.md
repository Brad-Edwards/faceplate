# Feature Specification: Frontend Test Setup

**Feature Branch**: `037-frontend-test-setup`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 022-frontend-shell

## User Scenarios & Testing

### User Story 1 - Vitest Configuration (Priority: P1)

Frontend tests run with Vitest.

**Why this priority**: Modern React testing.

**Independent Test**: Run vitest, verify it executes.

**Acceptance Scenarios**:

1. **Given** vitest installed, **When** npm test run, **Then** tests execute
2. **Given** tests exist, **When** run, **Then** results reported
3. **Given** vitest.config.ts, **When** run, **Then** settings applied

---

### User Story 2 - React Testing Library (Priority: P1)

Component tests use React Testing Library.

**Why this priority**: Standard React testing approach.

**Independent Test**: Test renders component, can query elements.

**Acceptance Scenarios**:

1. **Given** component test, **When** render called, **Then** component renders
2. **Given** rendered component, **When** screen queried, **Then** elements found
3. **Given** user event, **When** fireEvent called, **Then** event handled

---

### User Story 3 - Mock WebSocket (Priority: P1)

Tests can mock WebSocket connections.

**Why this priority**: Need to test without real backend.

**Independent Test**: Test uses mock WebSocket, verifies behavior.

**Acceptance Scenarios**:

1. **Given** mock WebSocket, **When** component connects, **Then** mock used
2. **Given** mock, **When** message sent, **Then** can verify message
3. **Given** mock, **When** message received, **Then** component updates

---

### Edge Cases

- What happens when import fails? → Clear error about missing module
- What happens with async components? → waitFor handles async updates

## Requirements

### Functional Requirements

- **FR-001**: System MUST use Vitest as test runner
- **FR-002**: System MUST use React Testing Library
- **FR-003**: System MUST provide WebSocket mock
- **FR-004**: System MUST use jsdom environment
- **FR-005**: System MUST provide setup file for common config
- **FR-006**: System SHOULD report coverage

### Key Files

- **vitest.config.ts**: Vitest configuration
- **src/test/setup.ts**: Test setup (mocks, etc.)
- **src/test/mocks/websocket.ts**: WebSocket mock

## Success Criteria

- **SC-001**: Vitest runs successfully
- **SC-002**: Components can be rendered and queried
- **SC-003**: WebSocket can be mocked

