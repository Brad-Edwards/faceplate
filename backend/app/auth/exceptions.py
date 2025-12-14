"""Authentication exceptions."""


class AuthError(Exception):
    """Base authentication error."""

    def __init__(self, message: str = "Authentication failed", error_code: str = "auth_error"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TokenExpiredError(AuthError):
    """Token has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message, error_code="token_expired")


class TokenInvalidError(AuthError):
    """Token is malformed or missing required claims."""

    def __init__(self, message: str = "Token is invalid"):
        super().__init__(message=message, error_code="token_invalid")


class TokenSignatureError(AuthError):
    """Token signature verification failed."""

    def __init__(self, message: str = "Token signature is invalid"):
        super().__init__(message=message, error_code="signature_invalid")


class JWKSFetchError(AuthError):
    """Failed to fetch JWKS from identity provider."""

    def __init__(self, message: str = "Failed to fetch public keys"):
        super().__init__(message=message, error_code="jwks_fetch_error")


class KeyNotFoundError(AuthError):
    """Key ID not found in JWKS."""

    def __init__(self, kid: str):
        super().__init__(message=f"Key not found: {kid}", error_code="key_not_found")
