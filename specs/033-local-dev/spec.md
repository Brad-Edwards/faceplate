# Feature Specification: Local Dev

**Feature Branch**: `033-local-dev`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 032-dockerfile, 001-database-schema

## User Scenarios & Testing

### User Story 1 - Docker Compose Setup (Priority: P1)

Developer can start full stack with one command.

**Why this priority**: Developer experience.

**Independent Test**: docker-compose up, verify all services start.

**Acceptance Scenarios**:

1. **Given** docker-compose.yml, **When** docker-compose up, **Then** all services start
2. **Given** services started, **When** checked, **Then** postgres, backend running
3. **Given** services running, **When** frontend accessed, **Then** app loads

---

### User Story 2 - Hot Reload (Priority: P1)

Code changes reflect without container restart.

**Why this priority**: Fast development iteration.

**Independent Test**: Change backend code, verify change takes effect.

**Acceptance Scenarios**:

1. **Given** backend running, **When** code changed, **Then** uvicorn reloads
2. **Given** frontend running, **When** code changed, **Then** Vite hot reloads
3. **Given** docker-compose, **When** volumes mounted, **Then** local code used

---

### User Story 3 - Database Persistence (Priority: P2)

Database data persists across restarts.

**Why this priority**: Don't lose dev data.

**Independent Test**: Add data, restart, verify data exists.

**Acceptance Scenarios**:

1. **Given** docker-compose, **When** postgres started, **Then** volume mounted
2. **Given** data in database, **When** docker-compose down/up, **Then** data persists
3. **Given** want fresh start, **When** volumes removed, **Then** clean database

---

### Edge Cases

- What happens when port already in use? → Clear error about port conflict
- What happens when docker not running? → Clear error message

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide docker-compose.yml for local development
- **FR-002**: System MUST include PostgreSQL service
- **FR-003**: System MUST mount source for hot reload
- **FR-004**: System MUST use volume for database persistence
- **FR-005**: System MUST expose ports for local access (8000, 5173)
- **FR-006**: System MUST provide .env.example for configuration

### Key Files

- **docker-compose.yml**: Development stack definition
- **.env.example**: Example environment variables
- **Makefile**: Convenience commands (make dev, make test, etc.)

## Success Criteria

- **SC-001**: Single command starts full stack
- **SC-002**: Hot reload works for both backend and frontend
- **SC-003**: Data persists across restarts

