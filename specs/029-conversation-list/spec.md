# Feature Specification: Conversation List

**Feature Branch**: `029-conversation-list`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 022-frontend-shell, 024-auth-flow

## User Scenarios & Testing

### User Story 1 - Display Conversations (Priority: P1)

Sidebar shows list of user's conversations.

**Why this priority**: Need to see and access conversations.

**Independent Test**: User has 5 conversations, verify all shown in sidebar.

**Acceptance Scenarios**:

1. **Given** user has conversations, **When** list loaded, **Then** conversations displayed
2. **Given** conversation in list, **When** displayed, **Then** shows title and updated time
3. **Given** no conversations, **When** list loaded, **Then** empty state shown

---

### User Story 2 - Create New Conversation (Priority: P1)

User can create new conversation.

**Why this priority**: Need to start new chats.

**Independent Test**: Click new button, verify new conversation created.

**Acceptance Scenarios**:

1. **Given** sidebar, **When** new button clicked, **Then** new conversation created
2. **Given** new conversation created, **When** complete, **Then** new conversation selected
3. **Given** new conversation, **When** created, **Then** appears at top of list

---

### User Story 3 - Current Conversation Highlight (Priority: P1)

Active conversation is visually highlighted.

**Why this priority**: User needs to know which conversation is active.

**Independent Test**: Select conversation, verify it's highlighted.

**Acceptance Scenarios**:

1. **Given** conversation selected, **When** displayed, **Then** highlighted in list
2. **Given** different conversation selected, **When** changes, **Then** highlight moves

---

### Edge Cases

- What happens with many conversations? → Scroll within sidebar
- What happens when title is very long? → Truncate with ellipsis

## Requirements

### Functional Requirements

- **FR-001**: System MUST display user's conversations in sidebar
- **FR-002**: System MUST sort conversations by most recent
- **FR-003**: System MUST provide button to create new conversation
- **FR-004**: System MUST highlight currently selected conversation
- **FR-005**: System MUST show conversation title and last updated
- **FR-006**: System MUST handle empty state

### Key UI Components

- **ConversationList**: Sidebar container
- **ConversationItem**: Single conversation in list
- **NewConversationButton**: Button to create new

## Success Criteria

- **SC-001**: Conversations displayed correctly
- **SC-002**: New conversation creation works
- **SC-003**: Current conversation highlighted

