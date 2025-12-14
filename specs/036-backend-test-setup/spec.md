# Feature Specification: Backend Test Setup

**Feature Branch**: `036-backend-test-setup`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 001-database-schema, 034-environment-config

## User Scenarios & Testing

### User Story 1 - Pytest Configuration (Priority: P1)

Backend tests run with pytest.

**Why this priority**: Constitution requires TDD.

**Independent Test**: Run pytest, verify it executes.

**Acceptance Scenarios**:

1. **Given** pytest installed, **When** pytest run, **Then** tests execute
2. **Given** tests exist, **When** pytest run, **Then** results reported
3. **Given** pytest.ini configured, **When** run, **Then** settings applied

---

### User Story 2 - Test Database (Priority: P1)

Tests use isolated test database.

**Why this priority**: Don't affect dev/prod data.

**Independent Test**: Run tests, verify prod database unchanged.

**Acceptance Scenarios**:

1. **Given** test config, **When** tests run, **Then** test database used
2. **Given** test database, **When** tests complete, **Then** cleaned up
3. **Given** parallel tests, **When** run, **Then** no database conflicts

---

### User Story 3 - Coverage Reporting (Priority: P1)

Tests report code coverage.

**Why this priority**: Constitution requires ≥80% coverage.

**Independent Test**: Run tests with coverage, verify report generated.

**Acceptance Scenarios**:

1. **Given** pytest-cov installed, **When** tests run, **Then** coverage reported
2. **Given** coverage below threshold, **When** CI runs, **Then** fails
3. **Given** coverage report, **When** generated, **Then** shows line-by-line coverage

---

### User Story 4 - Mock MCP Server (Priority: P1)

Tests have a mock MCP server for tool testing.

**Why this priority**: Can't test MCP integration without a server.

**Independent Test**: Call mock MCP tool, receive mock response.

**Acceptance Scenarios**:

1. **Given** mock MCP server fixture, **When** tool called, **Then** returns mock response
2. **Given** mock configured with tools, **When** list_tools called, **Then** returns configured tools
3. **Given** mock server, **When** any tool called, **Then** returns `{"result": "mock"}`

---

### Edge Cases

- What happens when database unavailable? → Tests that need DB are skipped
- What happens when test pollutes database? → Transaction rollback per test

## Requirements

### Functional Requirements

- **FR-001**: System MUST use pytest as test runner
- **FR-002**: System MUST use separate test database
- **FR-003**: System MUST report coverage with pytest-cov
- **FR-004**: System MUST fail CI if coverage < 80%
- **FR-005**: System MUST provide fixtures for common test needs
- **FR-006**: System MUST rollback transactions after each test
- **FR-007**: System MUST provide mock MCP server fixture
- **FR-008**: Mock MCP server MUST support list_tools and call_tool

### Mock MCP Server

Simple in-process mock that implements MCP protocol:

```python
@pytest.fixture
def mock_mcp_server():
    """Mock MCP server that returns configurable responses."""
    return MockMCPServer(tools=[
        {"name": "test_tool", "description": "A test tool"}
    ])
```

### Key Files

- **pyproject.toml**: pytest configuration
- **tests/conftest.py**: Shared fixtures
- **tests/factories.py**: Test data factories
- **tests/mocks/mcp_server.py**: Mock MCP server

## Success Criteria

- **SC-001**: pytest runs successfully
- **SC-002**: Test database isolated
- **SC-003**: Coverage reported and enforced

