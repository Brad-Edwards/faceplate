# Feature Specification: Conversation CRUD

**Feature Branch**: `005-conversation-crud`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 001-database-schema, 003-user-management

## User Scenarios & Testing

### User Story 1 - Create Conversation (Priority: P1)

User can create a new conversation.

**Why this priority**: Can't chat without a conversation.

**Independent Test**: Create conversation, verify it exists in database.

**Acceptance Scenarios**:

1. **Given** authenticated user, **When** create conversation requested, **Then** new conversation is created with user as owner
2. **Given** conversation created, **When** creation completes, **Then** conversation ID is returned
3. **Given** conversation created without title, **When** created, **Then** default title is assigned

---

### User Story 2 - Get Conversation (Priority: P1)

User can retrieve a specific conversation.

**Why this priority**: Need to load conversation to chat.

**Independent Test**: Create conversation, retrieve by ID, verify data matches.

**Acceptance Scenarios**:

1. **Given** user owns conversation, **When** retrieved by ID, **Then** conversation data is returned
2. **Given** user does not own conversation, **When** retrieved by ID, **Then** 403 forbidden
3. **Given** conversation doesn't exist, **When** retrieved by ID, **Then** 404 not found

---

### User Story 3 - Delete Conversation (Priority: P2)

User can delete their own conversations.

**Why this priority**: Important but not blocking for MVP.

**Independent Test**: Create conversation, delete it, verify it's gone.

**Acceptance Scenarios**:

1. **Given** user owns conversation, **When** delete requested, **Then** conversation and all messages are deleted
2. **Given** user does not own conversation, **When** delete requested, **Then** 403 forbidden

---

### Edge Cases

- What happens when deleting conversation with active WebSocket? → Delete proceeds, WebSocket continues until next action
- What happens when creating conversation with very long title? → Truncate to max length

## Requirements

### Functional Requirements

- **FR-001**: System MUST create conversations owned by requesting user
- **FR-002**: System MUST generate UUID for conversation ID
- **FR-003**: System MUST set created_at and updated_at timestamps
- **FR-004**: System MUST enforce ownership on read operations
- **FR-005**: System MUST cascade delete to messages on conversation delete
- **FR-006**: System MUST limit title length (max 255 characters)

### Key Entities

- **Conversation**: id, user_id, title, created_at, updated_at

## Success Criteria

- **SC-001**: Create operation under 100ms
- **SC-002**: Ownership enforced (verified by test)
- **SC-003**: Cascade delete works correctly

