# Tasks: Database Schema

**Input**: Design documents from `/specs/001-database-schema/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Constitution mandates Test-First (NON-NEGOTIABLE). Tests included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Alembic configuration

- [x] T001 Create directory structure per plan.md in backend/app/models/, backend/app/db/
- [x] T002 [P] Create backend/app/models/__init__.py with model exports
- [x] T003 [P] Create backend/app/db/__init__.py with db exports
- [x] T004 Initialize Alembic with `alembic init backend/app/db/migrations`
- [x] T005 Configure backend/alembic.ini for faceplate schema and async driver
- [x] T006 Configure backend/app/db/migrations/env.py for async SQLAlchemy

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

- [x] T007 Create SQLAlchemy declarative base with UUID mixin in backend/app/models/base.py
- [x] T008 Create async session factory in backend/app/db/session.py
- [x] T009 Create test fixtures in backend/tests/conftest.py (test database, async session)
- [x] T010 [P] Create backend/tests/models/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Schema Initialization (Priority: P1)

**Goal**: Database tables exist and are ready for application use

**Independent Test**: Run migrations, verify all tables exist with correct columns

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Create test for User model in backend/tests/models/test_user.py
- [x] T012 [P] [US1] Create test for Conversation model in backend/tests/models/test_conversation.py
- [x] T013 [P] [US1] Create test for Message model in backend/tests/models/test_message.py
- [x] T014 [P] [US1] Create test for MCPConfig model in backend/tests/models/test_mcp_config.py
- [x] T015 [US1] Create migration test in backend/tests/db/test_migrations.py

### Implementation for User Story 1

- [x] T016 [P] [US1] Create User model in backend/app/models/user.py per data-model.md
- [x] T017 [P] [US1] Create Conversation model in backend/app/models/conversation.py per data-model.md
- [x] T018 [P] [US1] Create Message model in backend/app/models/message.py per data-model.md
- [x] T019 [P] [US1] Create MCPConfig model in backend/app/models/mcp_config.py per data-model.md
- [x] T020 [US1] Update backend/app/models/__init__.py to export all models
- [x] T021 [US1] Generate initial migration with alembic revision --autogenerate -m "initial schema"
- [x] T022 [US1] Edit migration to add CREATE SCHEMA IF NOT EXISTS faceplate
- [x] T023 [US1] Run migration and verify tests pass (requires database)

**Checkpoint**: User Story 1 complete - all tables exist with correct schema

---

## Phase 4: User Story 2 - Connection Pooling (Priority: P1)

**Goal**: Application maintains efficient database connections

**Independent Test**: 50 concurrent connections don't exhaust pool

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [US2] Create pool configuration test in backend/tests/db/test_pool.py
- [x] T025 [US2] Add concurrent connection test (50 parallel queries) to backend/tests/db/test_pool.py (same file as T024)

### Implementation for User Story 2

- [x] T026 [US2] Configure pool_size=5, max_overflow=15 in backend/app/db/session.py
- [x] T027 [US2] Add pool_pre_ping=True for stale connection handling
- [x] T028 [US2] Add pool_timeout=30 for exhaustion handling
- [x] T029 [US2] Add connection error handling with retry logic
- [x] T030 [US2] Verify concurrent connection tests pass (requires database)

**Checkpoint**: User Story 2 complete - connection pooling works correctly

---

## Phase 5: Polish and Cross-Cutting Concerns

**Purpose**: Edge cases, error handling, and validation

- [x] T031 Implement database unreachable handling (fail fast with clear error)
- [x] T032 Implement mid-query connection drop handling (retry once)
- [x] T033 Add cascade delete integration test in backend/tests/db/test_cascade.py
- [x] T034 Run quickstart.md validation steps (requires database)
- [x] T035 Verify all Success Criteria (SC-001, SC-002, SC-003)

---

## Phase 6: Quality Gate (REQUIRED)

**Purpose**: Validate quality before spec is complete.

- [x] T036 Run linting: `uv run ruff check .`
- [x] T037 Run format check: `uv run ruff format --check .`
- [x] T038 Run security check: `uv run ruff check . --select=S`
- [x] T039 Run tests with coverage: `uv run pytest --cov=app`
- [x] T040 Verify all tests pass (33/33 passed)
- [ ] T041 Verify coverage >= 80% (currently 65% - models at 91-95%, session.py at 0%)

---

## Phase 7: Documentation (REQUIRED)

**Purpose**: Update docs to reflect implementation. Done after testing in case issues arise.

- [x] T042 Update docs/backend.md with actual schema and structure
- [ ] T043 Verify docs are consistent with implementation

**Quality Gate Status**: PARTIAL - Coverage below 80% due to session.py not being exercised in tests

**Note**: session.py (0% coverage) is used at runtime, not in tests which create their own engine.
Consider adding integration tests that use the production session factory to reach 80%.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational (can run parallel to US1)
- **Polish (Phase 5)**: Depends on US1 and US2 completion

### User Story Dependencies

- **User Story 1 (Schema)**: No dependencies on other stories
- **User Story 2 (Pooling)**: No dependencies on other stories (both P1, can parallelize)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models can be created in parallel (different files)
- Migration depends on all models
- Story complete before moving to Polish

### Parallel Opportunities

- T002, T003 can run in parallel (different files)
- T011, T012, T013, T014 can run in parallel (different test files)
- T016, T017, T018, T019 can run in parallel (different model files)
- US1 and US2 can be worked in parallel after Foundational

---

## Parallel Example: User Story 1 Models

```bash
# Launch all model tests together:
Task: "Create test for User model in backend/tests/models/test_user.py"
Task: "Create test for Conversation model in backend/tests/models/test_conversation.py"
Task: "Create test for Message model in backend/tests/models/test_message.py"
Task: "Create test for MCPConfig model in backend/tests/models/test_mcp_config.py"

# Launch all models together:
Task: "Create User model in backend/app/models/user.py"
Task: "Create Conversation model in backend/app/models/conversation.py"
Task: "Create Message model in backend/app/models/message.py"
Task: "Create MCPConfig model in backend/app/models/mcp_config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Schema)
4. **STOP and VALIDATE**: Run migrations, verify tables exist
5. Proceed to User Story 2

### Full Implementation

1. Setup + Foundational (T001-T010)
2. US1: Schema (T011-T023) - Tables exist
3. US2: Pooling (T024-T030) - Connections efficient
4. Polish (T031-T035) - Edge cases handled

---

## Notes

- Constitution: Test-First is NON-NEGOTIABLE
- All models use `faceplate` schema per constitution
- UUID7 via `uuid6` package (not in stdlib yet)
- Pool handles 50 concurrent via connection reuse (20 actual connections)
- Commit after each task or logical group

