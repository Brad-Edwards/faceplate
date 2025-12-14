# Feature Specification: Dockerfile

**Feature Branch**: `032-dockerfile`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: Backend and frontend specs complete

## User Scenarios & Testing

### User Story 1 - Build Image (Priority: P1)

Docker image can be built from source.

**Why this priority**: Required for deployment.

**Independent Test**: Run docker build, verify image created.

**Acceptance Scenarios**:

1. **Given** source code, **When** docker build run, **Then** image created successfully
2. **Given** image built, **When** inspected, **Then** contains backend and frontend
3. **Given** build fails, **When** error occurs, **Then** clear error message shown

---

### User Story 2 - Multi-Stage Build (Priority: P1)

Image uses multi-stage build for small size.

**Why this priority**: Smaller images deploy faster.

**Independent Test**: Verify final image doesn't contain dev dependencies.

**Acceptance Scenarios**:

1. **Given** multi-stage Dockerfile, **When** built, **Then** final image under 300MB
2. **Given** final image, **When** inspected, **Then** no dev tools included
3. **Given** build stages, **When** run, **Then** each stage cached independently

---

### User Story 3 - Run Container (Priority: P1)

Container can run successfully.

**Why this priority**: Must be able to run what we build.

**Independent Test**: docker run, verify app starts.

**Acceptance Scenarios**:

1. **Given** built image, **When** container started, **Then** app runs on port 8000
2. **Given** container running, **When** health check, **Then** returns healthy
3. **Given** container, **When** env vars provided, **Then** app uses them

---

### Edge Cases

- What happens when build fails mid-way? → Clear error, layer cached up to failure
- What happens when base image unavailable? → Fail with clear message

## Requirements

### Functional Requirements

- **FR-001**: System MUST use multi-stage build (builder + runtime)
- **FR-002**: System MUST build frontend in Node stage
- **FR-003**: System MUST install Python dependencies in builder stage
- **FR-004**: System MUST copy only necessary files to final stage
- **FR-005**: System MUST run as non-root user
- **FR-006**: System MUST expose port 8000
- **FR-007**: System MUST use slim base image (python:3.12-slim)

### Key Files

- **Dockerfile**: Multi-stage build definition
- **.dockerignore**: Exclude unnecessary files from build context

## Success Criteria

- **SC-001**: Image builds successfully
- **SC-002**: Final image under 300MB
- **SC-003**: Container runs and passes health check

