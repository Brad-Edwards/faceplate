# Feature Specification: Message Roles

**Feature Branch**: `008-message-roles`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 007-message-storage

## User Scenarios & Testing

### User Story 1 - User Messages (Priority: P1)

Messages from the user are marked with user role.

**Why this priority**: Core message type.

**Independent Test**: Save user message, verify role is "user".

**Acceptance Scenarios**:

1. **Given** user sends message, **When** saved, **Then** role is "user"
2. **Given** user message, **When** retrieved, **Then** role field is "user"

---

### User Story 2 - Assistant Messages (Priority: P1)

Messages from the LLM are marked with assistant role.

**Why this priority**: Core message type.

**Independent Test**: Save assistant message, verify role is "assistant".

**Acceptance Scenarios**:

1. **Given** LLM responds, **When** response saved, **Then** role is "assistant"
2. **Given** assistant message with tool_calls, **When** saved, **Then** role is "assistant" and tool_calls populated

---

### User Story 3 - Tool Messages (Priority: P1)

Tool results are stored as tool role messages.

**Why this priority**: Tool calling is core feature.

**Independent Test**: Save tool result message, verify role is "tool".

**Acceptance Scenarios**:

1. **Given** tool returns result, **When** saved, **Then** role is "tool"
2. **Given** tool message, **When** saved, **Then** content contains result and tool_call_id is tracked

---

### Edge Cases

- What happens with unknown role? → Validation error, reject save
- What happens with system role? → Not supported (system prompt is not persisted as message)

## Requirements

### Functional Requirements

- **FR-001**: System MUST support role values: user, assistant, tool
- **FR-002**: System MUST validate role on save (reject unknown roles)
- **FR-003**: System MUST NOT persist system role (system prompt is ephemeral)
- **FR-004**: System MUST associate tool messages with their tool_call_id
- **FR-005**: System MUST preserve role when retrieving messages

### Key Entities

- **MessageRole**: Enum of user, assistant, tool

## Success Criteria

- **SC-001**: Invalid roles rejected with validation error
- **SC-002**: All three roles can be saved and retrieved correctly
- **SC-003**: Tool messages linked to tool calls

