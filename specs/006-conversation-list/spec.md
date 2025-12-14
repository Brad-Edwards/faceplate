# Feature Specification: Conversation List

**Feature Branch**: `006-conversation-list`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 005-conversation-crud

## User Scenarios & Testing

### User Story 1 - List User's Conversations (Priority: P1)

User can see all their conversations.

**Why this priority**: Need to switch between conversations.

**Independent Test**: Create 3 conversations, list returns all 3.

**Acceptance Scenarios**:

1. **Given** user has conversations, **When** list requested, **Then** all user's conversations returned
2. **Given** user has no conversations, **When** list requested, **Then** empty list returned
3. **Given** other users have conversations, **When** list requested, **Then** only requesting user's conversations returned

---

### User Story 2 - Sorted by Recent (Priority: P1)

Conversations are sorted by most recently updated.

**Why this priority**: Most common access pattern.

**Independent Test**: Create 3 conversations, update middle one, verify it's first in list.

**Acceptance Scenarios**:

1. **Given** user has multiple conversations, **When** list requested, **Then** sorted by updated_at descending
2. **Given** new message added to conversation, **When** list requested, **Then** that conversation is first

---

### User Story 3 - Pagination (Priority: P3)

Large conversation lists can be paginated.

**Why this priority**: Nice to have, not blocking.

**Independent Test**: Create 50 conversations, request page 1 (20 items), verify 20 returned.

**Acceptance Scenarios**:

1. **Given** user has 50 conversations, **When** page 1 requested (limit 20), **Then** first 20 returned with has_more=true

---

### Edge Cases

- What happens with very large number of conversations? → Pagination handles it
- What happens if updated_at is same for multiple? → Secondary sort by created_at

## Requirements

### Functional Requirements

- **FR-001**: System MUST return only conversations owned by requesting user
- **FR-002**: System MUST sort by updated_at descending
- **FR-003**: System MUST include id, title, updated_at in list response
- **FR-004**: System SHOULD support pagination (limit, offset)
- **FR-005**: System MUST NOT include message content in list

### Key Entities

- **ConversationListItem**: id, title, updated_at (subset of Conversation)

## Success Criteria

- **SC-001**: List 100 conversations under 200ms
- **SC-002**: User isolation verified (no cross-user data)
- **SC-003**: Sort order correct

