# Feature Specification: Message Storage

**Feature Branch**: `007-message-storage`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 001-database-schema, 005-conversation-crud

## User Scenarios & Testing

### User Story 1 - Save Message (Priority: P1)

Messages are persisted to the database.

**Why this priority**: Can't have conversation history without persistence.

**Independent Test**: Save message, query database, verify it exists.

**Acceptance Scenarios**:

1. **Given** valid conversation, **When** message saved, **Then** message persisted with conversation_id
2. **Given** message saved, **When** saved, **Then** created_at timestamp is set
3. **Given** conversation doesn't exist, **When** message save attempted, **Then** foreign key error

---

### User Story 2 - Input Sanitization (Priority: P1)

User message content is sanitized before storage.

**Why this priority**: Security - prevent stored XSS and control character injection.

**Independent Test**: Save message with `<script>` tag, retrieve, verify escaped or stripped.

**Acceptance Scenarios**:

1. **Given** message with HTML tags, **When** saved, **Then** HTML is escaped or stripped
2. **Given** message with control characters, **When** saved, **Then** control characters removed
3. **Given** message with valid unicode, **When** saved, **Then** unicode preserved

---

### User Story 3 - Retrieve Messages (Priority: P1)

Messages can be retrieved for a conversation.

**Why this priority**: Need to load history on conversation switch.

**Independent Test**: Save 3 messages, retrieve all, verify order.

**Acceptance Scenarios**:

1. **Given** conversation with messages, **When** messages retrieved, **Then** all messages returned in order
2. **Given** conversation with no messages, **When** messages retrieved, **Then** empty list returned
3. **Given** messages retrieved, **When** returned, **Then** sorted by created_at ascending

---

### User Story 4 - Message with Tool Data (Priority: P1)

Messages can include tool call and result data.

**Why this priority**: Tool calling is core feature.

**Independent Test**: Save message with tool_calls JSON, retrieve, verify JSON intact.

**Acceptance Scenarios**:

1. **Given** message with tool_calls, **When** saved, **Then** tool_calls JSON preserved
2. **Given** message with tool_results, **When** saved, **Then** tool_results JSON preserved

---

### Edge Cases

- What happens with very large message content? → No limit (TEXT column)
- What happens with very large tool output? → Truncate at application level before save

## Requirements

### Functional Requirements

- **FR-001**: System MUST persist message with conversation_id, role, content
- **FR-002**: System MUST support tool_calls JSONB field (nullable)
- **FR-003**: System MUST support tool_results JSONB field (nullable)
- **FR-004**: System MUST set created_at on save
- **FR-005**: System MUST retrieve messages sorted by created_at ascending
- **FR-006**: System MUST update conversation.updated_at when message added
- **FR-007**: System MUST sanitize user message content (escape HTML, strip control chars)
- **FR-008**: System MUST preserve valid unicode in messages

### Key Entities

- **Message**: id, conversation_id, role, content, tool_calls, tool_results, created_at

## Success Criteria

- **SC-001**: Save message under 50ms
- **SC-002**: Retrieve 100 messages under 100ms
- **SC-003**: JSON fields stored and retrieved correctly

