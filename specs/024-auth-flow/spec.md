# Feature Specification: Auth Flow

**Feature Branch**: `024-auth-flow`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 022-frontend-shell

## User Scenarios & Testing

### User Story 1 - JWT from Cookie (Priority: P1)

Frontend retrieves JWT from cookie set by identity provider.

**Why this priority**: Auth integration with SSO.

**Independent Test**: Cookie present, verify JWT extracted.

**Acceptance Scenarios**:

1. **Given** JWT cookie present, **When** app loads, **Then** JWT extracted
2. **Given** JWT extracted, **When** WebSocket connects, **Then** JWT included in auth
3. **Given** no JWT cookie, **When** app loads, **Then** redirect to login

---

### User Story 2 - Auth State (Priority: P1)

Frontend tracks authentication state.

**Why this priority**: UI needs to know if user is authenticated.

**Independent Test**: Authenticated user, verify auth state is true.

**Acceptance Scenarios**:

1. **Given** valid JWT, **When** parsed, **Then** user info available in auth state
2. **Given** expired JWT, **When** detected, **Then** auth state reflects expiration
3. **Given** no JWT, **When** checked, **Then** auth state is unauthenticated

---

### User Story 3 - Login Redirect (Priority: P1)

Unauthenticated users are redirected to login.

**Why this priority**: Security - no anonymous access.

**Independent Test**: No JWT, verify redirect to login URL.

**Acceptance Scenarios**:

1. **Given** no JWT, **When** app loads, **Then** redirect to login URL
2. **Given** login successful, **When** returns with cookie, **Then** app loads normally

---

### User Story 4 - Token Expiration Handling (Priority: P1)

Frontend detects expired tokens and handles gracefully.

**Why this priority**: Users shouldn't be kicked out unexpectedly.

**Independent Test**: Token expires, verify user prompted to re-authenticate.

**Acceptance Scenarios**:

1. **Given** JWT about to expire (5 min), **When** detected, **Then** attempt silent refresh or warn user
2. **Given** JWT expired, **When** API call fails with 401, **Then** redirect to login
3. **Given** WebSocket disconnects due to auth, **When** reconnecting, **Then** check token validity first

---

### Edge Cases

- What happens when JWT expires mid-session? → Detect via exp claim, redirect to login
- What happens when cookie is malformed? → Treat as unauthenticated
- What happens when refresh fails? → Clear auth state, redirect to login

## Requirements

### Functional Requirements

- **FR-001**: System MUST read JWT from cookie
- **FR-002**: System MUST parse JWT claims for user info
- **FR-003**: System MUST track auth state (authenticated, unauthenticated, loading)
- **FR-004**: System MUST redirect unauthenticated users to login
- **FR-005**: System MUST provide user info to components via context/hook
- **FR-006**: System MUST NOT validate JWT signature (backend does this)
- **FR-007**: System MUST detect token expiration from exp claim
- **FR-008**: System MUST redirect to login on 401 responses
- **FR-009**: System SHOULD warn user before token expires (5 min warning)

### Key Entities

- **useAuth**: React hook for auth state
- **AuthState**: user, isAuthenticated, isLoading
- **User**: email, sub (from JWT claims)

## Success Criteria

- **SC-001**: JWT extracted from cookie
- **SC-002**: Auth state reflects JWT presence
- **SC-003**: Unauthenticated users redirected

