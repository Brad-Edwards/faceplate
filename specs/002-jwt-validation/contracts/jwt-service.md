# Contract: JWT Validation Service

**Feature**: 002-jwt-validation  
**Date**: 2025-12-14

## Service Interface

### JWTValidator

Primary service for validating Cognito JWTs.

#### Methods

##### `validate_token(token: str) -> TokenClaims`

Validates a JWT and returns extracted claims.

**Parameters**:
- `token`: Raw JWT string (without "Bearer " prefix)

**Returns**: `TokenClaims` dataclass with validated claims

**Raises**:
- `TokenExpiredError`: Token exp claim is in the past
- `TokenInvalidError`: Token is malformed or missing required claims
- `TokenSignatureError`: Signature validation failed
- `JWKSFetchError`: Could not retrieve public keys from Cognito

**Example**:
```python
validator = JWTValidator(settings)
claims = await validator.validate_token(token)
print(f"User: {claims.email}, ID: {claims.sub}")
```

##### `get_user_id(token: str) -> str`

Convenience method to extract just the user ID.

**Parameters**:
- `token`: Raw JWT string

**Returns**: The `sub` claim value

**Raises**: Same as `validate_token`

---

### JWKSCache

Manages Cognito public key caching.

#### Methods

##### `get_key(kid: str) -> RSAPublicKey`

Retrieves a public key by key ID.

**Parameters**:
- `kid`: Key ID from JWT header

**Returns**: RSA public key for signature verification

**Raises**:
- `KeyNotFoundError`: No key with given kid
- `JWKSFetchError`: Could not refresh keys

##### `refresh() -> None`

Forces a cache refresh from Cognito JWKS endpoint.

**Raises**:
- `JWKSFetchError`: Network or parsing error

---

## Data Types

### TokenClaims

```python
@dataclass
class TokenClaims:
    sub: str        # Cognito user ID
    email: str      # User email
    exp: int        # Expiration timestamp
    iat: int        # Issued-at timestamp
    iss: str        # Issuer URL
```

### Configuration

```python
class CognitoSettings(BaseSettings):
    cognito_region: str
    cognito_user_pool_id: str
    cognito_app_client_id: str
    
    @property
    def jwks_url(self) -> str:
        return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}/.well-known/jwks.json"
    
    @property
    def issuer(self) -> str:
        return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}"
```

## Error Responses

All auth errors return HTTP 401 with body:

```json
{
  "detail": "Authentication failed",
  "error": "token_expired|token_invalid|signature_invalid"
}
```

Note: Error messages are intentionally vague to prevent information leakage.

