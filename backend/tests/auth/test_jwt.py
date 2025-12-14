"""Tests for JWT validation."""

import time
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from app.auth.exceptions import (
    KeyNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TokenSignatureError,
)
from app.auth.jwt import JWTValidator, TokenClaims
from app.core.config import CognitoSettings

from .conftest import MockKeyPair

# =============================================================================
# User Story 1: Signature Validation Tests
# =============================================================================


class TestSignatureValidation:
    """Tests for JWT signature validation."""

    @pytest.fixture
    def cognito_settings(self, mock_cognito_settings: dict[str, str]) -> CognitoSettings:
        """Create CognitoSettings from mock values."""
        return CognitoSettings(**mock_cognito_settings)

    @pytest.fixture
    def validator(self, cognito_settings: CognitoSettings) -> JWTValidator:
        """Create a JWTValidator instance."""
        return JWTValidator(cognito_settings)

    async def test_valid_signature_passes(
        self,
        validator: JWTValidator,
        valid_token: str,
        mock_jwks: dict[str, Any],
    ) -> None:
        """T007: Valid token with correct signature passes validation."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            claims = await validator.validate_token(valid_token)

            assert claims is not None
            assert claims.sub == "test-user-123"
            assert claims.email == "test@example.com"

    async def test_tampered_signature_fails(
        self,
        validator: JWTValidator,
        tampered_token: str,
        mock_jwks: dict[str, Any],
        mock_key_pair: MockKeyPair,
    ) -> None:
        """T008: Token with tampered signature fails validation."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            with pytest.raises(TokenSignatureError):
                await validator.validate_token(tampered_token)

    async def test_unknown_key_fails(
        self,
        validator: JWTValidator,
        unknown_key_token: str,
        mock_jwks: dict[str, Any],
    ) -> None:
        """T009: Token signed by unknown key fails validation."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            with pytest.raises(KeyNotFoundError):
                await validator.validate_token(unknown_key_token)


# =============================================================================
# User Story 2: Claims Extraction Tests
# =============================================================================


class TestClaimsExtraction:
    """Tests for JWT claims extraction."""

    @pytest.fixture
    def cognito_settings(self, mock_cognito_settings: dict[str, str]) -> CognitoSettings:
        """Create CognitoSettings from mock values."""
        return CognitoSettings(**mock_cognito_settings)

    @pytest.fixture
    def validator(self, cognito_settings: CognitoSettings) -> JWTValidator:
        """Create a JWTValidator instance."""
        return JWTValidator(cognito_settings)

    async def test_claims_extraction(
        self,
        validator: JWTValidator,
        valid_token: str,
        mock_jwks: dict[str, Any],
        token_claims: dict[str, Any],
    ) -> None:
        """T014: Email and sub are correctly extracted from valid token."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            claims = await validator.validate_token(valid_token)

            assert isinstance(claims, TokenClaims)
            assert claims.sub == token_claims["sub"]
            assert claims.email == token_claims["email"]
            assert claims.iss == token_claims["iss"]
            assert claims.exp == token_claims["exp"]
            assert claims.iat == token_claims["iat"]

    async def test_missing_claims_fails(
        self,
        validator: JWTValidator,
        token_missing_claims: str,
        mock_jwks: dict[str, Any],
    ) -> None:
        """T015: Token missing required claims fails validation."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            with pytest.raises(TokenInvalidError, match=r"email|Missing required claim"):
                await validator.validate_token(token_missing_claims)

    async def test_expired_token_fails(
        self,
        validator: JWTValidator,
        expired_token: str,
        mock_jwks: dict[str, Any],
    ) -> None:
        """T016: Expired token fails validation."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            with pytest.raises(TokenExpiredError):
                await validator.validate_token(expired_token)


# =============================================================================
# Additional Validation Tests
# =============================================================================


class TestTokenValidation:
    """Additional token validation tests."""

    @pytest.fixture
    def cognito_settings(self, mock_cognito_settings: dict[str, str]) -> CognitoSettings:
        """Create CognitoSettings from mock values."""
        return CognitoSettings(**mock_cognito_settings)

    @pytest.fixture
    def validator(self, cognito_settings: CognitoSettings) -> JWTValidator:
        """Create a JWTValidator instance."""
        return JWTValidator(cognito_settings)

    async def test_get_user_id(
        self,
        validator: JWTValidator,
        valid_token: str,
        mock_jwks: dict[str, Any],
    ) -> None:
        """Test get_user_id convenience method."""
        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            user_id = await validator.get_user_id(valid_token)
            assert user_id == "test-user-123"

    async def test_malformed_token_fails(
        self,
        validator: JWTValidator,
    ) -> None:
        """Test that malformed tokens are rejected."""
        with pytest.raises(TokenInvalidError):
            await validator.validate_token("not-a-valid-jwt")

    async def test_wrong_issuer_fails(
        self,
        validator: JWTValidator,
        mock_key_pair: MockKeyPair,
        mock_jwks: dict[str, Any],
    ) -> None:
        """Test that tokens with wrong issuer are rejected."""
        from jose import jwt

        claims = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iss": "https://wrong-issuer.com",  # Wrong issuer
            "aud": "test-client-id",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = jwt.encode(
            claims,
            mock_key_pair.get_private_pem(),
            algorithm="RS256",
            headers={"kid": mock_key_pair.kid},
        )

        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            with pytest.raises(TokenInvalidError, match=r"issuer|iss"):
                await validator.validate_token(token)

    async def test_wrong_audience_fails(
        self,
        validator: JWTValidator,
        mock_key_pair: MockKeyPair,
        mock_jwks: dict[str, Any],
    ) -> None:
        """Test that tokens with wrong audience are rejected."""
        from jose import jwt

        claims = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_TestPool",
            "aud": "wrong-client-id",  # Wrong audience
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = jwt.encode(
            claims,
            mock_key_pair.get_private_pem(),
            algorithm="RS256",
            headers={"kid": mock_key_pair.kid},
        )

        with patch.object(validator, "_fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            with pytest.raises(TokenInvalidError, match=r"audience|aud"):
                await validator.validate_token(token)
