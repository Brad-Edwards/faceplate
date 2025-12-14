# Feature Specification: Agent Orchestrator

**Feature Branch**: `014-agent-orchestrator`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 013-context-builder, 010-streaming-response, 011-stream-to-websocket

## User Scenarios & Testing

### User Story 1 - Process User Message (Priority: P1)

System processes user message through complete agent loop.

**Why this priority**: Core orchestration of the entire flow.

**Independent Test**: Send message, verify LLM called, response streamed, message saved.

**Acceptance Scenarios**:

1. **Given** user sends message, **When** processed, **Then** message saved, context built, LLM called
2. **Given** LLM responds with text, **When** complete, **Then** response streamed and saved
3. **Given** LLM responds with tool call, **When** detected, **Then** tool executed and loop continues

---

### User Story 2 - Tool Call Loop (Priority: P1)

System executes tools and continues LLM conversation.

**Why this priority**: Tool calling is core feature.

**Independent Test**: LLM requests tool, tool executes, result sent to LLM, LLM responds.

**Acceptance Scenarios**:

1. **Given** LLM returns tool call, **When** processed, **Then** tool is executed
2. **Given** tool returns result, **When** received, **Then** result added to context and LLM called again
3. **Given** LLM returns text after tool, **When** processed, **Then** text streamed to user

---

### User Story 3 - Iteration Control (Priority: P1)

System limits tool call iterations.

**Why this priority**: Prevent runaway loops.

**Independent Test**: Force 25 tool calls, verify loop stops after limit.

**Acceptance Scenarios**:

1. **Given** max iterations configured, **When** limit reached, **Then** loop stops with message to user
2. **Given** loop stopped by limit, **When** notified, **Then** user informed of limit

---

### Edge Cases

- What happens when tool execution fails? → Pass error to LLM as result
- What happens when LLM returns both text and tool call? → Stream text, then execute tool

## Requirements

### Functional Requirements

- **FR-001**: System MUST save user message before processing
- **FR-002**: System MUST build context and call LLM
- **FR-003**: System MUST stream text responses to WebSocket
- **FR-004**: System MUST execute tool calls and continue loop
- **FR-005**: System MUST save assistant response after completion
- **FR-006**: System MUST enforce max iteration limit
- **FR-007**: System MUST handle mixed text/tool responses

### Key Entities

- **AgentOrchestrator**: Main loop coordinator
- **AgentState**: Current state of agent loop (iteration count, etc.)

## Success Criteria

- **SC-001**: Complete loop executes correctly (text response)
- **SC-002**: Tool calling loop works (call → result → continue)
- **SC-003**: Iteration limit enforced

