# Feature Specification: Message Input

**Feature Branch**: `026-message-input`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 022-frontend-shell, 023-websocket-hook

## User Scenarios & Testing

### User Story 1 - Text Input (Priority: P1)

User can type messages in input field.

**Why this priority**: Core input mechanism.

**Independent Test**: Type text, verify it appears in input.

**Acceptance Scenarios**:

1. **Given** input field, **When** user types, **Then** text appears in field
2. **Given** text in field, **When** user clicks send, **Then** message sent and field cleared
3. **Given** empty field, **When** user clicks send, **Then** nothing happens

---

### User Story 2 - Keyboard Shortcuts (Priority: P1)

Enter sends message, Shift+Enter adds newline.

**Why this priority**: Standard chat UX.

**Independent Test**: Press Enter, verify message sent.

**Acceptance Scenarios**:

1. **Given** text in field, **When** Enter pressed, **Then** message sent
2. **Given** text in field, **When** Shift+Enter pressed, **Then** newline added
3. **Given** message sent, **When** complete, **Then** input field cleared

---

### User Story 3 - Disabled State (Priority: P1)

Input disabled when not connected or waiting for response.

**Why this priority**: Prevent confusion during processing.

**Independent Test**: Disconnect WebSocket, verify input disabled.

**Acceptance Scenarios**:

1. **Given** WebSocket disconnected, **When** rendered, **Then** input disabled with message
2. **Given** waiting for response, **When** rendered, **Then** send button shows loading
3. **Given** reconnected, **When** rendered, **Then** input enabled

---

### Edge Cases

- What happens with very long input? → Textarea expands (up to limit)
- What happens when paste large text? → Accept up to reasonable limit

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide text input for messages
- **FR-002**: System MUST send message on Enter key
- **FR-003**: System MUST add newline on Shift+Enter
- **FR-004**: System MUST clear input after send
- **FR-005**: System MUST disable input when disconnected
- **FR-006**: System MUST show loading state during send
- **FR-007**: System MUST support multi-line input (textarea)

### Key UI Components

- **MessageInput**: Input field with send button
- **SendButton**: Button that shows loading state

## Success Criteria

- **SC-001**: Text input works
- **SC-002**: Keyboard shortcuts work
- **SC-003**: Disabled state reflects connection

