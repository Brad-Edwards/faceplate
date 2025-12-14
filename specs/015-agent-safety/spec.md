# Feature Specification: Agent Safety

**Feature Branch**: `015-agent-safety`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 014-agent-orchestrator

## User Scenarios & Testing

### User Story 1 - Max Tool Calls Per Turn (Priority: P1)

System limits total tool calls per user message.

**Why this priority**: Prevent cost/resource runaway.

**Independent Test**: Configure max 20 tools, trigger 25, verify stopped at 20.

**Acceptance Scenarios**:

1. **Given** max_tool_calls=20, **When** 20 calls made, **Then** loop stops
2. **Given** limit reached, **When** stopped, **Then** user notified of limit

---

### User Story 2 - Max Consecutive Tools (Priority: P1)

System limits consecutive tool calls without text response.

**Why this priority**: Prevent infinite tool loops.

**Independent Test**: 10 consecutive tools without text, verify stopped.

**Acceptance Scenarios**:

1. **Given** max_consecutive_tools=10, **When** 10 consecutive tools, **Then** loop stops
2. **Given** text response between tools, **When** received, **Then** consecutive counter resets

---

### User Story 3 - Rate Limiting (Priority: P2)

System limits messages per user per time period.

**Why this priority**: Prevent abuse, control costs.

**Independent Test**: Send 101 messages in 1 hour, verify 101st rejected.

**Acceptance Scenarios**:

1. **Given** rate limit 100/hour, **When** 100 messages sent, **Then** all succeed
2. **Given** rate limit exceeded, **When** next message sent, **Then** rejected with 429 error
3. **Given** rate limit period expires, **When** new period, **Then** counter resets

---

### Edge Cases

- What happens when safety limit hit mid-tool? → Complete current tool, then stop
- What happens when rate limit bypassed by multiple connections? → Limit is per-user, not per-connection

## Requirements

### Functional Requirements

- **FR-001**: System MUST enforce max tool calls per turn (configurable, default 20)
- **FR-002**: System MUST enforce max consecutive tools (configurable, default 10)
- **FR-003**: System SHOULD enforce message rate limit per user (configurable)
- **FR-004**: System MUST notify user when limits reached
- **FR-005**: System MUST log when limits are hit
- **FR-006**: System MUST reset consecutive counter on text response

### Key Entities

- **SafetyLimits**: Configuration for all limits
- **UserRateLimit**: Tracks user's message rate

## Success Criteria

- **SC-001**: Tool limits enforced correctly
- **SC-002**: Consecutive tool detection works
- **SC-003**: Rate limiting prevents abuse

