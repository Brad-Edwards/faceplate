# Feature Specification: Tool Persistence

**Feature Branch**: `021-tool-persistence`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 007-message-storage, 020-tool-execution

## User Scenarios & Testing

### User Story 1 - Save Tool Calls (Priority: P1)

Tool calls are persisted with messages.

**Why this priority**: Need history for context and debugging.

**Independent Test**: Execute tool, verify tool_calls saved in message.

**Acceptance Scenarios**:

1. **Given** assistant message with tool call, **When** saved, **Then** tool_calls JSON includes call details
2. **Given** multiple tool calls, **When** saved, **Then** all calls in tool_calls array
3. **Given** tool call details, **When** saved, **Then** name, arguments, id preserved

---

### User Story 2 - Save Tool Results (Priority: P1)

Tool results are persisted.

**Why this priority**: Need history for context and debugging.

**Independent Test**: Execute tool, verify result saved.

**Acceptance Scenarios**:

1. **Given** tool execution completes, **When** result saved, **Then** tool_results JSON populated
2. **Given** tool result, **When** saved, **Then** result content and tool_call_id preserved
3. **Given** tool error, **When** saved, **Then** error message preserved

---

### User Story 3 - Reload Tool History (Priority: P1)

Tool history is included when reloading conversation.

**Why this priority**: LLM needs tool history for context.

**Independent Test**: Reload conversation, verify tool calls and results in context.

**Acceptance Scenarios**:

1. **Given** conversation with tools, **When** reloaded, **Then** tool_calls in messages
2. **Given** conversation with results, **When** reloaded, **Then** tool_results in messages

---

### Edge Cases

- What happens with very large tool result? → Truncate before save
- What happens when save fails? → Log error, don't crash agent loop

## Requirements

### Functional Requirements

- **FR-001**: System MUST save tool_calls in assistant message
- **FR-002**: System MUST save tool_results in tool message
- **FR-003**: System MUST preserve tool_call_id linking calls to results
- **FR-004**: System MUST include tool history in context reload
- **FR-005**: System MUST handle save failures gracefully
- **FR-006**: System MUST truncate large results before save

### Key Entities

- **ToolCallRecord**: Persisted tool call (id, name, arguments)
- **ToolResultRecord**: Persisted tool result (tool_call_id, content, error)

## Success Criteria

- **SC-001**: Tool calls saved correctly
- **SC-002**: Tool results saved correctly
- **SC-003**: History reloads include tools

