# Feature Specification: MCP Config Management

**Feature Branch**: `040-mcp-config-management`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 001-database-schema

## User Scenarios & Testing

### User Story 1 - Add MCP Server (Priority: P1)

User can add an MCP server configuration.

**Why this priority**: Users need to connect to their MCP servers.

**Independent Test**: Add server config, verify saved.

**Acceptance Scenarios**:

1. **Given** user authenticated, **When** adds MCP server, **Then** config saved
2. **Given** server config, **When** added, **Then** includes name, transport, auth details
3. **Given** duplicate name, **When** added, **Then** rejected with error

---

### User Story 2 - List MCP Servers (Priority: P1)

User can see their configured MCP servers.

**Why this priority**: Users need to see what's configured.

**Independent Test**: Add 3 servers, list shows all 3.

**Acceptance Scenarios**:

1. **Given** user has servers, **When** listed, **Then** all user's servers shown
2. **Given** server in list, **When** displayed, **Then** shows name and status (connected/disconnected)
3. **Given** user A, **When** lists, **Then** user B's servers not shown

---

### User Story 3 - Edit MCP Server (Priority: P1)

User can update MCP server configuration.

**Why this priority**: Fix misconfigurations.

**Independent Test**: Edit server URL, verify updated.

**Acceptance Scenarios**:

1. **Given** existing server, **When** edited, **Then** changes saved
2. **Given** server edited, **When** next connection, **Then** new config used
3. **Given** invalid edit, **When** saved, **Then** validation error shown

---

### User Story 4 - Delete MCP Server (Priority: P1)

User can remove an MCP server.

**Why this priority**: Remove unused servers.

**Independent Test**: Delete server, verify gone.

**Acceptance Scenarios**:

1. **Given** existing server, **When** deleted, **Then** removed from list
2. **Given** server deleted, **When** deleted, **Then** associated credentials removed

---

### User Story 5 - Test Connection (Priority: P2)

User can test MCP server connection.

**Why this priority**: Verify config before using.

**Independent Test**: Test connection, verify success/failure shown.

**Acceptance Scenarios**:

1. **Given** valid config, **When** test clicked, **Then** connection test runs
2. **Given** successful test, **When** complete, **Then** success message shown
3. **Given** failed test, **When** complete, **Then** error details shown

---

### Edge Cases

- What happens when server unreachable during add? → Allow save, show warning
- What happens when editing active server? → Reconnect on next request

## Requirements

### Functional Requirements

- **FR-001**: System MUST support CRUD operations on MCP server configs
- **FR-002**: System MUST validate config format before save
- **FR-003**: System MUST encrypt credentials at rest
- **FR-004**: System MUST isolate configs per user
- **FR-005**: System MUST support multiple servers per user
- **FR-006**: System SHOULD support connection testing
- **FR-007**: System MUST track connection status per server

### MCP Server Config Schema

```json
{
  "id": "uuid",
  "name": "my-kali-server",
  "transport": "ssh",
  "config": {
    "host": "10.1.1.10",
    "port": 22,
    "username": "kali"
  },
  "auth": {
    "type": "key",
    "key_id": "ref-to-encrypted-key"
  },
  "enabled": true,
  "created_at": "2025-12-13T12:00:00Z"
}
```

## Success Criteria

- **SC-001**: CRUD operations work correctly
- **SC-002**: Credentials encrypted
- **SC-003**: User isolation enforced

