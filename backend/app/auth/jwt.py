"""JWT validation for Cognito tokens."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import structlog
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import CognitoSettings

from .exceptions import (
    KeyNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TokenSignatureError,
)

if TYPE_CHECKING:
    from .jwks import JWKSCache

logger = structlog.get_logger(__name__)


@dataclass
class TokenClaims:
    """Extracted claims from a validated JWT."""

    sub: str  # Cognito user ID
    email: str  # User email
    exp: int  # Expiration timestamp
    iat: int  # Issued-at timestamp
    iss: str  # Issuer URL


class JWTValidator:
    """Validates Cognito JWT tokens."""

    def __init__(
        self,
        settings: CognitoSettings,
        jwks_cache: "JWKSCache | None" = None,
    ) -> None:
        """Initialize the validator with Cognito settings.

        Args:
            settings: Cognito configuration including region, pool ID, and client ID.
            jwks_cache: Optional JWKSCache instance for key retrieval.
        """
        self._settings = settings
        self._jwks_cache_instance = jwks_cache
        self._inline_jwks: dict[str, Any] | None = None

    async def validate_token(self, token: str) -> TokenClaims:
        """Validate a JWT and return extracted claims.

        Args:
            token: Raw JWT string (without "Bearer " prefix).

        Returns:
            TokenClaims with validated user information.

        Raises:
            TokenExpiredError: Token has expired.
            TokenInvalidError: Token is malformed or missing required claims.
            TokenSignatureError: Signature validation failed.
            KeyNotFoundError: Key ID not found in JWKS.
        """
        # Basic token structure check
        if not token or token.count(".") != 2:
            raise TokenInvalidError("Malformed token")

        try:
            # Get the key ID from token header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                raise TokenInvalidError("Token missing key ID")

            # Get the signing key
            key = await self._get_signing_key(kid)

            # Verify and decode the token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self._settings.cognito_app_client_id,
                issuer=self._settings.issuer,
                options={"require_exp": True, "require_iat": True},
            )

            # Validate required claims
            return self._extract_claims(payload)

        except ExpiredSignatureError as e:
            logger.warning("token_expired", error=str(e))
            raise TokenExpiredError() from e
        except JWTError as e:
            error_msg = str(e).lower()
            if "signature" in error_msg:
                logger.warning("signature_invalid", error=str(e))
                raise TokenSignatureError() from e
            if "issuer" in error_msg or "iss" in error_msg:
                logger.warning("invalid_issuer", error=str(e))
                raise TokenInvalidError("Invalid issuer") from e
            if "audience" in error_msg or "aud" in error_msg:
                logger.warning("invalid_audience", error=str(e))
                raise TokenInvalidError("Invalid audience") from e
            logger.warning("token_invalid", error=str(e))
            raise TokenInvalidError(str(e)) from e

    async def get_user_id(self, token: str) -> str:
        """Extract just the user ID from a token.

        Args:
            token: Raw JWT string.

        Returns:
            The subject (sub) claim value.

        Raises:
            Same exceptions as validate_token.
        """
        claims = await self.validate_token(token)
        return claims.sub

    async def _get_signing_key(self, kid: str) -> dict[str, Any]:
        """Get the signing key for a given key ID.

        Args:
            kid: Key ID from JWT header.

        Returns:
            JWK dict for signature verification.

        Raises:
            KeyNotFoundError: Key ID not in JWKS.
        """
        # Use JWKSCache if available
        if self._jwks_cache_instance is not None:
            return await self._jwks_cache_instance.get_key(kid)

        # Fall back to inline JWKS (for testing)
        jwks = await self._fetch_jwks()

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key

        logger.warning("key_not_found", kid=kid)
        raise KeyNotFoundError(kid)

    async def _fetch_jwks(self) -> dict[str, Any]:
        """Fetch JWKS from Cognito.

        This method can be overridden in tests.

        Returns:
            JWKS dict with keys array.
        """
        # This is for testing - return inline cache if set
        if self._inline_jwks is not None:
            return self._inline_jwks
        return {"keys": []}

    def _extract_claims(self, payload: dict[str, Any]) -> TokenClaims:
        """Extract and validate required claims from token payload.

        Args:
            payload: Decoded JWT payload.

        Returns:
            TokenClaims with extracted values.

        Raises:
            TokenInvalidError: Required claim is missing.
        """
        required_claims = ["sub", "email", "exp", "iat", "iss"]

        for claim in required_claims:
            if claim not in payload:
                logger.warning("missing_claim", claim=claim)
                raise TokenInvalidError(f"Missing required claim: {claim}")

        return TokenClaims(
            sub=payload["sub"],
            email=payload["email"],
            exp=payload["exp"],
            iat=payload["iat"],
            iss=payload["iss"],
        )
