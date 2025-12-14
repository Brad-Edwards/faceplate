# Feature Specification: User Management

**Feature Branch**: `003-user-management`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 001-database-schema, 002-jwt-validation

## User Scenarios & Testing

### User Story 1 - User Creation on First Login (Priority: P1)

New users are automatically created in the database on first access.

**Why this priority**: Users shouldn't have to register separately.

**Independent Test**: First connection with valid JWT creates user record.

**Acceptance Scenarios**:

1. **Given** valid JWT for unknown user, **When** user connects, **Then** user record is created with email and subject_id
2. **Given** valid JWT for existing user, **When** user connects, **Then** existing user record is returned
3. **Given** user creation fails, **When** database error, **Then** connection is rejected with 500 error

---

### User Story 2 - User Lookup (Priority: P1)

System can retrieve user by subject ID or email.

**Why this priority**: Need to associate data with users.

**Independent Test**: Lookup by subject_id returns correct user.

**Acceptance Scenarios**:

1. **Given** existing user, **When** looked up by subject_id, **Then** user is returned
2. **Given** non-existent user, **When** looked up, **Then** None is returned (not error)

---

### Edge Cases

- What happens when email changes in identity provider? → subject_id is authoritative, update email on login
- What happens when two requests race to create same user? → Handle unique constraint, return existing user

## Requirements

### Functional Requirements

- **FR-001**: System MUST create user on first authenticated access
- **FR-002**: System MUST use subject_id as unique identifier (not email)
- **FR-003**: System MUST update email if changed in identity provider
- **FR-004**: System MUST handle concurrent creation attempts gracefully
- **FR-005**: System MUST store created_at timestamp

### Key Entities

- **User**: Authenticated user (id, email, subject_id, created_at)

## Success Criteria

- **SC-001**: User creation completes in under 100ms
- **SC-002**: Concurrent creation attempts don't cause errors
- **SC-003**: All users have valid subject_id (never null)

