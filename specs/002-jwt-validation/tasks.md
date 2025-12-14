# Tasks: JWT Validation

**Input**: Design documents from `/specs/002-jwt-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

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

**Purpose**: Project structure and configuration for auth module

- [x] T001 Create auth module directory structure: `backend/app/auth/__init__.py`
- [x] T002 [P] Create auth exceptions module in `backend/app/auth/exceptions.py`
- [x] T003 [P] Add Cognito settings to `backend/app/core/config.py`

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that MUST be complete before user stories

- [x] T004 Create test fixtures for JWT testing in `backend/tests/auth/conftest.py`
- [x] T005 [P] Create mock JWKS generator for tests in `backend/tests/auth/conftest.py`
- [x] T006 [P] Create mock JWT generator for tests in `backend/tests/auth/conftest.py`

**Checkpoint**: Test infrastructure ready - user story implementation can begin

---

## Phase 3: User Story 1 - Signature Validation (Priority: P1)

**Goal**: System validates JWT signatures against identity provider's public keys

**Independent Test**: Valid token passes, token with tampered signature fails

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Test valid signature passes in `backend/tests/auth/test_jwt.py::test_valid_signature_passes`
- [x] T008 [P] [US1] Test tampered signature fails in `backend/tests/auth/test_jwt.py::test_tampered_signature_fails`
- [x] T009 [P] [US1] Test unknown key fails in `backend/tests/auth/test_jwt.py::test_unknown_key_fails`

### Implementation for User Story 1

- [x] T010 [US1] Create JWTValidator class in `backend/app/auth/jwt.py`
- [x] T011 [US1] Implement `validate_token()` method with RS256 verification in `backend/app/auth/jwt.py`
- [x] T012 [US1] Add issuer (iss) claim validation in `backend/app/auth/jwt.py`
- [x] T013 [US1] Add audience (aud) claim validation in `backend/app/auth/jwt.py`

**Checkpoint**: Signature validation works - tokens with valid signatures pass, invalid fail

---

## Phase 4: User Story 2 - Claims Extraction (Priority: P1)

**Goal**: System extracts user identity from JWT claims

**Independent Test**: Extract email and subject ID from valid token

### Tests for User Story 2

- [x] T014 [P] [US2] Test email and sub extraction in `backend/tests/auth/test_jwt.py::test_claims_extraction`
- [x] T015 [P] [US2] Test missing required claims fails in `backend/tests/auth/test_jwt.py::test_missing_claims_fails`
- [x] T016 [P] [US2] Test expired token fails in `backend/tests/auth/test_jwt.py::test_expired_token_fails`

### Implementation for User Story 2

- [x] T017 [US2] Create TokenClaims dataclass in `backend/app/auth/jwt.py`
- [x] T018 [US2] Implement claims extraction in `validate_token()` in `backend/app/auth/jwt.py`
- [x] T019 [US2] Add expiration (exp) claim validation in `backend/app/auth/jwt.py`
- [x] T020 [US2] Add `get_user_id()` convenience method in `backend/app/auth/jwt.py`

**Checkpoint**: Claims extraction works - can get email and sub from valid tokens

---

## Phase 5: User Story 3 - Key Caching (Priority: P1)

**Goal**: System caches identity provider public keys for performance

**Independent Test**: Second validation uses cached keys, no network call

### Tests for User Story 3

- [x] T021 [P] [US3] Test keys are fetched on first call in `backend/tests/auth/test_jwks.py::test_keys_fetched_on_first_call`
- [x] T022 [P] [US3] Test cached keys used within TTL in `backend/tests/auth/test_jwks.py::test_cached_keys_used`
- [x] T023 [P] [US3] Test keys refresh after TTL expires in `backend/tests/auth/test_jwks.py::test_keys_refresh_after_ttl`
- [x] T024 [P] [US3] Test graceful degradation when IdP down in `backend/tests/auth/test_jwks.py::test_idp_down_uses_cache`

### Implementation for User Story 3

- [x] T025 [US3] Create JWKSCache class in `backend/app/auth/jwks.py`
- [x] T026 [US3] Implement async JWKS fetch with httpx in `backend/app/auth/jwks.py`
- [x] T027 [US3] Add TTL-based cache expiration (1 hour) in `backend/app/auth/jwks.py`
- [x] T028 [US3] Implement `get_key(kid)` method in `backend/app/auth/jwks.py`
- [x] T029 [US3] Integrate JWKSCache with JWTValidator in `backend/app/auth/jwt.py`
- [x] T030 [US3] Handle JWKS fetch errors gracefully in `backend/app/auth/jwks.py`

**Checkpoint**: Key caching works - network calls minimized, graceful degradation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 [P] Add structured logging for auth events in `backend/app/auth/jwt.py`
- [x] T032 [P] Export public API in `backend/app/auth/__init__.py`
- [x] T033 Run quickstart.md validation scenarios

---

## Phase 7: Quality Gate (REQUIRED)

**Purpose**: Validate quality before spec is complete

- [x] T034 Run linting: `cd backend && uv run ruff check .`
- [x] T035 Run format check: `cd backend && uv run ruff format --check .`
- [x] T036 Run security check: `cd backend && uv run ruff check . --select=S`
- [x] T037 Run tests with coverage: `cd backend && uv run pytest tests/auth/ --cov=app/auth --cov-fail-under=80`
- [x] T038 Verify all tests pass (no failures)
- [x] T039 Verify coverage >= 80%
- [x] T040 Fix any issues found above before proceeding

---

## Phase 8: Documentation (REQUIRED)

**Purpose**: Update docs to reflect implementation

- [x] T041 Update `docs/backend.md` with auth module documentation
- [x] T042 Add JWT validation section to `docs/security.md`
- [x] T043 Verify docs are consistent with implementation

**Quality Gate Criteria**:

| Check | Command | Required |
|-------|---------|----------|
| Lint | `ruff check .` | 0 errors |
| Format | `ruff format --check .` | 0 errors |
| Security | `ruff check . --select=S` | 0 errors |
| Tests | `pytest tests/auth/` | All pass |
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

- **User Story 1 (Signature Validation)**: No dependencies on other stories
- **User Story 2 (Claims Extraction)**: Builds on US1 (same file, sequential)
- **User Story 3 (Key Caching)**: Builds on US1/US2 (integrates with validator)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation follows test requirements
- Story complete before moving to next

### Parallel Opportunities

- T002, T003 can run in parallel (different files)
- T005, T006 can run in parallel (same file but independent fixtures)
- T007, T008, T009 can run in parallel (independent test cases)
- T014, T015, T016 can run in parallel (independent test cases)
- T021, T022, T023, T024 can run in parallel (independent test cases)
- T031, T032 can run in parallel (different concerns)

---

## Parallel Example: User Story 3 Tests

```bash
# Launch all tests for User Story 3 together:
Task T021: "Test keys are fetched on first call"
Task T022: "Test cached keys used within TTL"
Task T023: "Test keys refresh after TTL expires"
Task T024: "Test graceful degradation when IdP down"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Signature Validation)
4. **STOP and VALIDATE**: Tokens can be validated
5. Continue to US2 and US3

### Incremental Delivery

1. Setup + Foundational → Test infrastructure ready
2. User Story 1 → Can validate signatures
3. User Story 2 → Can extract user identity
4. User Story 3 → Production-ready with caching
5. Quality Gate → Verified quality standards

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 43 |
| Setup Tasks | 3 |
| Foundational Tasks | 3 |
| US1 Tasks | 7 |
| US2 Tasks | 7 |
| US3 Tasks | 10 |
| Polish Tasks | 3 |
| Quality Gate Tasks | 7 |
| Documentation Tasks | 3 |
| Parallel Opportunities | 15 tasks |

**MVP Scope**: Complete through User Story 1 (T001-T013) for basic signature validation.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- All user stories are P1 priority per spec (all required for MVP)
- TDD required per constitution
- Commit after each task or logical group

