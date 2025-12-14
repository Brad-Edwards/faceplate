# Feature Specification: MCP User Auth

**Feature Branch**: `018-mcp-user-auth`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 016-mcp-client, 040-mcp-config-management

**Scope Clarification**: This spec covers *using* per-user credentials at runtime. Spec 040 covers CRUD operations on MCP server configs. This spec covers how credentials are retrieved and used when making MCP connections.

## User Scenarios & Testing

### User Story 1 - Per-User MCP Connection (Priority: P1)

When user makes a tool call, their specific MCP credentials are used.

**Why this priority**: Constitution requires per-user MCP auth.

**Independent Test**: Two users with different configs, each connects with their own credentials.

**Acceptance Scenarios**:

1. **Given** user has MCP config, **When** tool called, **Then** connection uses user's credentials
2. **Given** user A and user B, **When** both call tools, **Then** each uses their own credentials
3. **Given** user has no MCP config, **When** tool called, **Then** graceful error (no tools available)

---

### User Story 2 - Credential Retrieval (Priority: P1)

System retrieves decrypted credentials when establishing MCP connection.

**Why this priority**: Credentials must be decrypted at runtime.

**Independent Test**: Stored encrypted credential, verify decrypted for connection.

**Acceptance Scenarios**:

1. **Given** encrypted credential in DB, **When** MCP connection needed, **Then** credential decrypted
2. **Given** decrypted credential, **When** connection established, **Then** credential passed to MCP SDK

---

### User Story 3 - OAuth Token Handling (Priority: P2)

System handles OAuth tokens for MCP servers that require OAuth.

**Why this priority**: MCP SDK supports OAuth.

**Technical Note**: Uses MCP SDK's `OAuthClientProvider` with `TokenStorage` interface. Tokens stored in DB via 040-mcp-config-management.

**Acceptance Scenarios**:

1. **Given** MCP server requires OAuth, **When** connecting, **Then** OAuth flow initiated
2. **Given** OAuth token stored, **When** connecting, **Then** stored token used
3. **Given** OAuth token expired, **When** refresh token available, **Then** token refreshed

---

### Edge Cases

- What happens when credentials are invalid? → MCP connection fails, error surfaced to user
- What happens when no config exists? → Tools for that server unavailable

## Requirements

### Functional Requirements

- **FR-001**: System MUST retrieve user's MCP config on tool call
- **FR-002**: System MUST decrypt credentials before use (encryption key from env)
- **FR-003**: System MUST pass credentials to MCP SDK connection
- **FR-004**: System MUST support MCP OAuth flow via SDK
- **FR-005**: System MUST NOT expose credentials in logs or error messages
- **FR-006**: System MUST isolate credentials (user A can't trigger user B's connection)

### Key Entities

- **MCPCredentialStore**: Retrieves and decrypts credentials
- **UserMCPSession**: Per-user MCP connection with user's credentials

## Success Criteria

- **SC-001**: Per-user credential isolation verified
- **SC-002**: Credentials never logged
- **SC-003**: OAuth flow works with SDK
