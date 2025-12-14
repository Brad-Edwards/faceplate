# Feature Specification: Tool Filtering

**Feature Branch**: `041-tool-filtering`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 019-tool-discovery, 005-conversation-crud

## User Scenarios & Testing

### User Story 1 - Disable Tools Per Conversation (Priority: P1)

User can disable specific tools for a conversation.

**Why this priority**: Control what tools are available in each context.

**Independent Test**: Disable tool X in conversation A, verify tool X not available.

**Acceptance Scenarios**:

1. **Given** conversation, **When** tool disabled, **Then** tool not provided to LLM
2. **Given** tool disabled, **When** LLM tries to call, **Then** tool not in available list
3. **Given** conversation A has tool disabled, **When** conversation B checked, **Then** tool still available in B

---

### User Story 2 - Tool List UI (Priority: P1)

User can see available tools and toggle them.

**Why this priority**: Users need UI to control tools.

**Independent Test**: Open tool settings, see list with toggles.

**Acceptance Scenarios**:

1. **Given** conversation open, **When** tool settings opened, **Then** all available tools listed
2. **Given** tool in list, **When** displayed, **Then** shows name, description, enabled status
3. **Given** toggle clicked, **When** changed, **Then** setting saved immediately

---

### User Story 3 - Default Tool Settings (Priority: P2)

User can set default enabled/disabled tools.

**Why this priority**: Don't reconfigure every conversation.

**Independent Test**: Set default, new conversation has that default.

**Acceptance Scenarios**:

1. **Given** default tool settings, **When** new conversation created, **Then** defaults applied
2. **Given** defaults set, **When** conversation overrides, **Then** override takes precedence

---

### User Story 4 - Tool Filtering Persists (Priority: P1)

Tool settings persist across sessions.

**Why this priority**: Don't lose configuration.

**Independent Test**: Disable tool, close app, reopen, tool still disabled.

**Acceptance Scenarios**:

1. **Given** tool disabled, **When** conversation reloaded, **Then** still disabled
2. **Given** tool settings, **When** stored, **Then** saved with conversation

---

### Edge Cases

- What happens when tool no longer exists? → Remove from settings, ignore
- What happens when all tools disabled? → Allow, LLM works without tools

## Requirements

### Functional Requirements

- **FR-001**: System MUST support per-conversation tool filtering
- **FR-002**: System MUST persist tool settings with conversation
- **FR-003**: System MUST filter tools before providing to LLM
- **FR-004**: System MUST show available tools in UI
- **FR-005**: System SHOULD support default tool settings per user
- **FR-006**: System MUST handle missing tools gracefully

### Data Model Addition

```sql
-- Add to conversations table or separate table
conversation_tool_settings JSONB DEFAULT '{}'

-- Format:
{
  "disabled_tools": ["kali_execute_command", "victim_read_file"],
  "enabled_only": false  -- if true, only explicitly enabled tools work
}
```

### API

- `GET /conversations/:id/tools` - List tools with enabled status
- `PATCH /conversations/:id/tools/:tool_name` - Enable/disable tool

## Success Criteria

- **SC-001**: Tools can be disabled per conversation
- **SC-002**: Settings persist correctly
- **SC-003**: Disabled tools not available to LLM

