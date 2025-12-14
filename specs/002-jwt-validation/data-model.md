# Data Model: JWT Validation

**Feature**: 002-jwt-validation  
**Date**: 2025-12-14

## Overview

JWT validation is a stateless operation. No database entities are created by this spec. The module operates on in-memory data structures only.

## Runtime Data Structures

### JWKSCache

In-memory cache for Cognito public keys.

```
JWKSCache
├── keys: dict[str, RSAPublicKey]   # kid -> public key mapping
├── fetched_at: datetime            # When keys were last fetched
└── ttl: int                        # Cache duration in seconds (3600)
```

**Lifecycle**:
- Created on first validation request
- Refreshed when TTL expires
- Cleared on application restart

### TokenClaims

Extracted claims from validated JWT.

```
TokenClaims
├── sub: str          # Cognito subject (user ID)
├── email: str        # User email address
├── exp: int          # Expiration timestamp
├── iat: int          # Issued-at timestamp
└── iss: str          # Issuer URL
```

**Usage**: Passed to downstream handlers after successful validation.

## Database Impact

None. This spec does not modify the database schema.

## Relationship to Other Specs

- **001-database-schema**: Users table has `subject_id` column that stores the `sub` claim
- **003-user-session**: Will use TokenClaims to create/update user records
- **004-websocket-core**: Will call JWT validator on connection

