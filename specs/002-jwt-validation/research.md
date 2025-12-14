# Research: JWT Validation

**Feature**: 002-jwt-validation  
**Date**: 2025-12-14

## Decision Log

### 1. JWT Library Selection

**Decision**: Use `python-jose[cryptography]` for JWT validation

**Rationale**:
- Already in project dependencies (from spec 001 scaffold)
- Supports RS256 algorithm required by Cognito
- Mature library with good async compatibility
- Cryptography backend provides secure key handling

**Alternatives Considered**:
- `PyJWT`: Simpler but less feature-rich for JWKS handling
- `authlib`: More complex, overkill for our needs
- Manual validation: Security risk, not recommended

### 2. JWKS Fetching Strategy

**Decision**: Use `httpx` async client with in-memory TTL cache

**Rationale**:
- httpx is already a project dependency
- Async fetch doesn't block event loop
- Simple dict-based cache with timestamp sufficient
- 1-hour TTL balances freshness with performance

**Alternatives Considered**:
- `requests`: Blocking, not suitable for async FastAPI
- Redis cache: Violates constitution (no Redis)
- No caching: Unacceptable latency per request

### 3. Cognito JWKS Endpoint

**Decision**: Fetch from `https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json`

**Rationale**:
- Standard Cognito endpoint format
- Region and pool_id from environment config
- Returns RSA public keys in JWK format

**Configuration Required**:
- `COGNITO_REGION`: AWS region (e.g., us-east-1)
- `COGNITO_USER_POOL_ID`: User pool identifier
- `COGNITO_APP_CLIENT_ID`: For audience validation

### 4. Claim Validation

**Decision**: Validate exp, aud, iss claims; extract email and sub

**Rationale**:
- `exp`: Reject expired tokens (standard JWT)
- `aud`: Must match our app client ID
- `iss`: Must match Cognito issuer URL
- `email`: User identifier for display/logging
- `sub`: Stable user ID for database FK

**Edge Cases**:
- Missing email claim: Reject (required for our use case)
- Token without exp: Reject (security requirement)

### 5. Error Handling Strategy

**Decision**: Raise specific exceptions, return 401 with error hints

**Rationale**:
- Specific exceptions allow fine-grained logging
- 401 status for all auth failures (don't leak details)
- Include general error category in response (expired, invalid, etc.)

**Exception Hierarchy**:
- `AuthError` (base)
  - `TokenExpiredError`
  - `TokenInvalidError`
  - `TokenSignatureError`
  - `JWKSFetchError`

## Open Questions

None. All technical decisions resolved.

