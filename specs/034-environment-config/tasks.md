# Tasks: Environment Config

**Input**: Design documents from `/specs/034-environment-config/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: REQUIRED per constitution (Test-First, 80% coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `backend/tests/`

---

## Phase 1: Setup

**Purpose**: Test infrastructure for config module

- [x] T001 Create test directory structure: `backend/tests/core/__init__.py`
- [x] T002 [P] Create test fixtures for config in `backend/tests/core/conftest.py`

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that MUST be complete before user stories

- [x] T003 Add BedrockSettings class to `backend/app/core/config.py`
- [x] T004 [P] Add remaining config fields to Settings class in `backend/app/core/config.py`

**Checkpoint**: Config classes defined - user story implementation can begin

---

## Phase 3: User Story 1 - Environment Variables (Priority: P1)

**Goal**: Application reads configuration from environment

**Independent Test**: Set env var, verify app uses it

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] [US1] Test config loads from environment in `backend/tests/core/test_config.py::test_loads_from_env`
- [x] T006 [P] [US1] Test defaults used when optional vars missing in `backend/tests/core/test_config.py::test_defaults`
- [x] T007 [P] [US1] Test invalid value raises validation error in `backend/tests/core/test_config.py::test_invalid_value`

### Implementation for User Story 1

- [x] T008 [US1] Implement environment variable parsing in `backend/app/core/config.py`
- [x] T009 [US1] Add type validation for all config fields in `backend/app/core/config.py`
- [x] T010 [US1] Add default values for optional fields in `backend/app/core/config.py`

**Checkpoint**: Config loads from environment - defaults work, types validated

---

## Phase 4: User Story 2 - Required vs Optional (Priority: P1)

**Goal**: Required config causes startup failure if missing

**Independent Test**: Omit required var, verify startup fails with clear message

### Tests for User Story 2

- [x] T011 [P] [US2] Test missing required var fails in `backend/tests/core/test_config.py::test_required_missing_fails`
- [x] T012 [P] [US2] Test all required vars present succeeds in `backend/tests/core/test_config.py::test_required_present_succeeds`
- [x] T013 [P] [US2] Test error message is descriptive in `backend/tests/core/test_config.py::test_error_message`

### Implementation for User Story 2

- [x] T014 [US2] Mark required fields (no defaults) in `backend/app/core/config.py`
- [x] T015 [US2] Ensure validation error includes field name in `backend/app/core/config.py`

**Checkpoint**: Missing required config fails fast with clear message

---

## Phase 5: User Story 3 - Secrets from Secrets Manager (Priority: P2)

**Goal**: Sensitive config can come from Secrets Manager

**Independent Test**: Configure secrets manager path, verify value retrieved

### Tests for User Story 3

- [x] T016 [P] [US3] Test secrets manager fetch in `backend/tests/core/test_secrets.py::test_fetch_secret`
- [x] T017 [P] [US3] Test fallback to env var in `backend/tests/core/test_secrets.py::test_fallback_to_env`
- [x] T018 [P] [US3] Test timeout/retry behavior in `backend/tests/core/test_secrets.py::test_timeout_retry`

### Implementation for User Story 3

- [x] T019 [US3] Create secrets module in `backend/app/core/secrets.py`
- [x] T020 [US3] Implement Secrets Manager client wrapper in `backend/app/core/secrets.py`
- [x] T021 [US3] Add retry logic for transient failures in `backend/app/core/secrets.py`
- [x] T022 [US3] Integrate secrets with Settings class in `backend/app/core/config.py`
- [x] T023 [US3] Use SecretStr for sensitive values in `backend/app/core/config.py`

**Checkpoint**: Secrets can be fetched from Secrets Manager with fallback

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T024 [P] Ensure sensitive values not logged (SecretStr) in `backend/app/core/config.py`
- [x] T025 [P] Add config documentation to `backend/app/core/config.py` docstrings
- [x] T026 Run quickstart.md validation scenarios

---

## Phase 7: Quality Gate (REQUIRED)

**Purpose**: Validate quality before spec is complete

- [x] T027 Run linting: `cd backend && uv run ruff check .`
- [x] T028 Run format check: `cd backend && uv run ruff format --check .`
- [x] T029 Run security check: `cd backend && uv run ruff check . --select=S`
- [x] T030 Run tests with coverage: `cd backend && uv run pytest tests/core/ --cov=app/core --cov-fail-under=80`
- [x] T031 Verify all tests pass (no failures)
- [x] T032 Verify coverage >= 80%
- [x] T033 Fix any issues found above before proceeding

---

## Phase 8: Documentation (REQUIRED)

**Purpose**: Update docs to reflect implementation

- [x] T034 Update `docs/backend.md` with config module documentation
- [x] T035 Add environment variables table to `docs/deployment.md`
- [x] T036 Verify docs are consistent with implementation

**Quality Gate Criteria**:

| Check | Command | Required |
|-------|---------|----------|
| Lint | `ruff check .` | 0 errors |
| Format | `ruff format --check .` | 0 errors |
| Security | `ruff check . --select=S` | 0 errors |
| Tests | `pytest tests/core/` | All pass |
| Coverage | `--cov-fail-under=80` | >= 80% |

**Checkpoint**: Quality gate passed - spec implementation complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3-5)**: Depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all user stories complete
- **Quality Gate (Phase 7)**: Depends on Polish complete
- **Documentation (Phase 8)**: Depends on Quality Gate passed

### User Story Dependencies

- **User Story 1 (Environment Variables)**: No dependencies on other stories
- **User Story 2 (Required vs Optional)**: Builds on US1 (same file, sequential)
- **User Story 3 (Secrets Manager)**: Can run parallel to US1/US2 (separate file)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation follows test requirements
- Story complete before moving to next

### Parallel Opportunities

- T001, T002 can run in parallel (different files)
- T003, T004 can run in parallel (independent config sections)
- T005, T006, T007 can run in parallel (independent test cases)
- T011, T012, T013 can run in parallel (independent test cases)
- T016, T017, T018 can run in parallel (independent test cases)
- T024, T025 can run in parallel (different concerns)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Environment Variables)
4. **STOP and VALIDATE**: Config loads from env vars
5. Continue to US2 and US3

### Incremental Delivery

1. Setup + Foundational -> Config classes defined
2. User Story 1 -> Basic env var loading works
3. User Story 2 -> Required validation enforced
4. User Story 3 -> Secrets Manager integration (optional for MVP)
5. Quality Gate -> Verified quality standards

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 36 |
| Setup Tasks | 2 |
| Foundational Tasks | 2 |
| US1 Tasks | 6 |
| US2 Tasks | 5 |
| US3 Tasks | 8 |
| Polish Tasks | 3 |
| Quality Gate Tasks | 7 |
| Documentation Tasks | 3 |
| Parallel Opportunities | 14 tasks |

**MVP Scope**: Complete through User Story 2 (T001-T015) for core config validation.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- US1 and US2 are P1 priority (required for MVP)
- US3 is P2 priority (production enhancement)
- TDD required per constitution
- Commit after each task or logical group

