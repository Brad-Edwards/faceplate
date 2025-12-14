# Feature Specification: Tool Display

**Feature Branch**: `028-tool-display`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 025-message-list, 027-streaming-render

## User Scenarios & Testing

### User Story 1 - Tool Call Display (Priority: P1)

Tool calls are displayed distinctly from text.

**Why this priority**: User needs to see what tools are being called.

**Independent Test**: Tool call received, verify distinct display.

**Acceptance Scenarios**:

1. **Given** tool_call chunk, **When** received, **Then** tool call displayed with name and arguments
2. **Given** tool call displayed, **When** rendered, **Then** visually distinct from text (box, icon, etc.)
3. **Given** tool arguments, **When** displayed, **Then** formatted as readable JSON/code

---

### User Story 2 - Tool Result Display (Priority: P1)

Tool results are displayed after tool calls.

**Why this priority**: User needs to see tool output.

**Independent Test**: Tool result received, verify displayed with tool call.

**Acceptance Scenarios**:

1. **Given** tool_result chunk, **When** received, **Then** result displayed
2. **Given** tool result, **When** displayed, **Then** associated with its tool call
3. **Given** large tool result, **When** displayed, **Then** truncated with expand option

---

### User Story 3 - Tool Error Display (Priority: P1)

Tool errors are displayed clearly.

**Why this priority**: User needs to know when tools fail.

**Independent Test**: Tool error received, verify error displayed.

**Acceptance Scenarios**:

1. **Given** tool error result, **When** received, **Then** error displayed with styling
2. **Given** error display, **When** rendered, **Then** visually indicates error (red, icon, etc.)

---

### Edge Cases

- What happens with very long tool output? → Collapsible with "show more"
- What happens with special characters in output? → Escape for safe display

## Requirements

### Functional Requirements

- **FR-001**: System MUST display tool calls distinctly from text
- **FR-002**: System MUST show tool name and arguments
- **FR-003**: System MUST display tool results
- **FR-004**: System MUST visually link tool calls to their results
- **FR-005**: System MUST display tool errors with error styling
- **FR-006**: System MUST handle large outputs (truncate/collapse)
- **FR-007**: System MUST safely render output (escape HTML)

### Key UI Components

- **ToolCall**: Display component for tool calls
- **ToolResult**: Display component for tool results
- **ToolError**: Display component for tool errors

## Success Criteria

- **SC-001**: Tool calls visually distinct
- **SC-002**: Results displayed correctly
- **SC-003**: Errors clearly indicated

