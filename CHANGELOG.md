# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-12-14

### Added

- JWT validation for Cognito tokens (spec 002)
- JWKS caching with 1-hour TTL
- Graceful degradation when IdP unreachable

## [0.2.0] - 2025-12-14

### Added

- Database schema (spec 001) - users, conversations, messages, MCP configs
- Alembic migrations for PostgreSQL
- Connection pooling with retry logic
- Comprehensive test suite for database layer
- Quality gate validation phase in Spec Kit workflow

### Changed

- CI pipeline now enforces 80% coverage and lint checks as hard gates
- Separated backend and frontend CI jobs for parallel execution

## [0.1.0] - 2025-12-13

### Added

- Initial project setup with Spec Kit
- 41 specifications covering full agentic chat implementation
- Backend scaffold (FastAPI, SQLAlchemy, MCP)
- Frontend scaffold (React 19, Vite, TypeScript)
- CI/CD pipeline with quality checks
- SonarCloud integration
- Branch protection for main and dev

