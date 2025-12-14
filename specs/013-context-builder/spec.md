# Feature Specification: Context Builder

**Feature Branch**: `013-context-builder`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 007-message-storage, 008-message-roles

## User Scenarios & Testing

### User Story 1 - Build Conversation Context (Priority: P1)

System builds message array for LLM from conversation history.

**Why this priority**: LLM needs context to respond appropriately.

**Independent Test**: Create conversation with 5 messages, build context, verify all included.

**Acceptance Scenarios**:

1. **Given** conversation with messages, **When** context built, **Then** all messages included in order
2. **Given** messages with roles, **When** context built, **Then** roles correctly mapped
3. **Given** empty conversation, **When** context built, **Then** only system prompt included

---

### User Story 2 - System Prompt Injection (Priority: P1)

System prompt is included at start of context.

**Why this priority**: System prompt defines agent behavior.

**Independent Test**: Build context, verify system prompt is first.

**Acceptance Scenarios**:

1. **Given** context built, **When** completed, **Then** system prompt is first message with role "system"
2. **Given** system prompt configured, **When** context built, **Then** configured prompt is used

---

### User Story 3 - Tool Message Formatting (Priority: P1)

Tool calls and results are correctly formatted for LLM.

**Why this priority**: LLM needs tool history to continue reasoning.

**Technical Note**: Using OpenAI format via BAG. Tool calls are in assistant message's `tool_calls` array. Tool results are messages with role "tool" and `tool_call_id` reference.

**Independent Test**: Context includes tool call and result, verify format.

**Acceptance Scenarios**:

1. **Given** assistant message with tool_calls, **When** context built, **Then** `tool_calls` array included with id, function.name, function.arguments
2. **Given** tool result message, **When** context built, **Then** formatted as role "tool" with `tool_call_id` and `content`

---

### Edge Cases

- What happens with very long context? → Truncate oldest messages (keep system prompt)
- What happens with missing tool result? → Include tool call, LLM will handle

## Requirements

### Functional Requirements

- **FR-001**: System MUST include system prompt as first message
- **FR-002**: System MUST include all conversation messages in order
- **FR-003**: System MUST map message roles to LLM-expected format
- **FR-004**: System MUST include tool_calls in assistant messages
- **FR-005**: System MUST format tool results per LLM specification
- **FR-006**: System SHOULD truncate context if exceeding token limit (future)

### Key Entities

- **ContextBuilder**: Builds message array from conversation
- **LLMMessage**: Message formatted for LLM API

## Success Criteria

- **SC-001**: Context built in under 50ms for 100 messages
- **SC-002**: All message roles correctly mapped
- **SC-003**: Tool messages correctly formatted

