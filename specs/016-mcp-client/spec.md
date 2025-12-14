# Feature Specification: MCP Client

**Feature Branch**: `016-mcp-client`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 040-mcp-config-management

**Technical Context**: Uses `mcp` Python SDK (v1.24.0+). Supports multiple transports: `stdio`, `streamable_http`. For Shifter integration, MCP servers run as separate processes (accessed via stdio) or as HTTP services.

## User Scenarios & Testing

### User Story 1 - MCP SDK Integration (Priority: P1)

System uses MCP SDK for server communication.

**Why this priority**: Foundation for all MCP features.

**Independent Test**: Initialize MCP client, verify SDK loaded.

**Acceptance Scenarios**:

1. **Given** MCP SDK available, **When** client initialized, **Then** client ready for connections
2. **Given** client initialized, **When** server config provided, **Then** can connect to server

---

### User Story 2 - Connection Management (Priority: P1)

System manages connections to MCP servers.

**Why this priority**: Need reliable server connections.

**Independent Test**: Connect to server, send request, disconnect cleanly.

**Acceptance Scenarios**:

1. **Given** server config, **When** connect requested, **Then** connection established
2. **Given** active connection, **When** disconnect requested, **Then** connection closed cleanly
3. **Given** connection lost, **When** detected, **Then** reconnection attempted

---

### User Story 3 - Multiple Servers (Priority: P1)

System can connect to multiple MCP servers simultaneously.

**Why this priority**: Different tools on different servers.

**Independent Test**: Connect to 2 servers, call tool on each.

**Acceptance Scenarios**:

1. **Given** multiple server configs, **When** initialized, **Then** all servers connected
2. **Given** tool call for server A, **When** requested, **Then** routed to server A
3. **Given** one server fails, **When** other healthy, **Then** healthy server continues working

---

### Edge Cases

- What happens when server is slow to connect? → Timeout after configured limit
- What happens when server disconnects unexpectedly? → Reconnect with backoff

## Requirements

### Functional Requirements

- **FR-001**: System MUST use official `mcp` Python SDK (v1.24.0+)
- **FR-002**: System MUST support multiple simultaneous server connections
- **FR-003**: System MUST manage connection lifecycle (connect, disconnect, reconnect)
- **FR-004**: System MUST route requests to appropriate server based on tool name
- **FR-005**: System MUST handle connection failures gracefully
- **FR-006**: System MUST support connection timeout configuration
- **FR-007**: System MUST support `stdio` transport (subprocess with stdin/stdout)
- **FR-008**: System MUST support `streamable_http` transport (HTTP endpoint)
- **FR-009**: System SHOULD support OAuth authentication for MCP servers (via SDK's OAuthClientProvider)

### Key Entities

- **MCPClientManager**: Manages multiple MCP server connections per user
- **MCPServerConnection**: Single connection wrapping `mcp.ClientSession`
- **MCPTransportConfig**: Configuration for stdio or HTTP transport

## Success Criteria

- **SC-001**: SDK integration works correctly
- **SC-002**: Multiple server support verified
- **SC-003**: Connection failures handled gracefully

