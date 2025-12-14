# Feature Specification: Conversation Switch

**Feature Branch**: `030-conversation-switch`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 029-conversation-list, 025-message-list

## User Scenarios & Testing

### User Story 1 - Switch Conversation (Priority: P1)

Clicking conversation in list loads it.

**Why this priority**: Need to switch between chats.

**Independent Test**: Click different conversation, verify messages change.

**Acceptance Scenarios**:

1. **Given** conversation in list, **When** clicked, **Then** that conversation's messages load
2. **Given** switch, **When** complete, **Then** URL updates to /chat/:id
3. **Given** switch, **When** loading, **Then** loading indicator shown

---

### User Story 2 - Load History (Priority: P1)

Conversation history loads when switched.

**Why this priority**: Need to see previous messages.

**Independent Test**: Switch to conversation with messages, verify history shown.

**Acceptance Scenarios**:

1. **Given** conversation with history, **When** loaded, **Then** all messages displayed
2. **Given** history loaded, **When** complete, **Then** scrolled to bottom
3. **Given** load fails, **When** error, **Then** error message shown

---

### User Story 3 - Context Isolation (Priority: P1)

Switching conversations clears current context.

**Why this priority**: Constitution requires context isolation.

**Independent Test**: Conversation A active, switch to B, verify A's context cleared.

**Acceptance Scenarios**:

1. **Given** conversation A active, **When** switch to B, **Then** A's messages not visible
2. **Given** switch complete, **When** new message sent, **Then** only B's context used

---

### Edge Cases

- What happens when switching while streaming? → Cancel stream, switch anyway
- What happens when conversation is deleted? → Remove from list, select another

## Requirements

### Functional Requirements

- **FR-001**: System MUST load conversation messages on selection
- **FR-002**: System MUST update URL on conversation switch
- **FR-003**: System MUST clear previous conversation from view
- **FR-004**: System MUST show loading state during switch
- **FR-005**: System MUST handle switch during active stream
- **FR-006**: System MUST scroll to bottom after loading history

### Key Entities

- **ConversationContext**: Current conversation state
- **useConversation**: Hook for conversation management

## Success Criteria

- **SC-001**: Switch loads correct messages
- **SC-002**: Context isolation maintained
- **SC-003**: URL reflects current conversation

