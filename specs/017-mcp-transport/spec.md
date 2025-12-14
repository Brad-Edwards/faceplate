# Feature Specification: MCP Transport

**Feature Branch**: `017-mcp-transport`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 016-mcp-client

## User Scenarios & Testing

### User Story 1 - SSH Transport (Priority: P1)

System communicates with MCP servers over SSH.

**Why this priority**: SSH is primary transport for remote servers.

**Independent Test**: Connect to MCP server via SSH, execute tool.

**Acceptance Scenarios**:

1. **Given** SSH credentials, **When** connection requested, **Then** SSH session established
2. **Given** SSH connection, **When** MCP request sent, **Then** response received via SSH
3. **Given** SSH key authentication, **When** key provided, **Then** authentication succeeds

---

### User Story 2 - Stdio Transport (Priority: P2)

System communicates with local MCP servers via stdio.

**Why this priority**: Useful for local development.

**Independent Test**: Launch local MCP server, communicate via stdio.

**Acceptance Scenarios**:

1. **Given** local server binary, **When** launched, **Then** stdio communication works
2. **Given** stdio connection, **When** request sent, **Then** response received

---

### User Story 3 - Transport Selection (Priority: P1)

System selects transport based on server configuration.

**Why this priority**: Different servers need different transports.

**Independent Test**: Configure SSH server and stdio server, both work.

**Acceptance Scenarios**:

1. **Given** server config with transport=ssh, **When** connected, **Then** SSH used
2. **Given** server config with transport=stdio, **When** connected, **Then** stdio used

---

### Edge Cases

- What happens when SSH connection drops? → Reconnect with same credentials
- What happens when SSH key is invalid? → Clear error message

## Requirements

### Functional Requirements

- **FR-001**: System MUST support SSH transport for remote servers
- **FR-002**: System SHOULD support stdio transport for local servers
- **FR-003**: System MUST select transport based on server config
- **FR-004**: System MUST support SSH key authentication
- **FR-005**: System MUST handle transport-specific errors
- **FR-006**: System MUST support configurable SSH timeout

### Key Entities

- **Transport**: Abstract transport interface
- **SSHTransport**: SSH-based transport implementation
- **StdioTransport**: Local stdio transport implementation

## Success Criteria

- **SC-001**: SSH transport works with key auth
- **SC-002**: Transport selection works correctly
- **SC-003**: Transport errors surfaced appropriately

