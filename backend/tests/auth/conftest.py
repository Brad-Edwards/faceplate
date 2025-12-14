"""Test fixtures for JWT validation testing."""

import time
from dataclasses import dataclass
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt


@dataclass
class MockKeyPair:
    """RSA key pair for testing."""

    kid: str
    private_key: rsa.RSAPrivateKey
    public_key: rsa.RSAPublicKey

    def get_private_pem(self) -> bytes:
        """Get private key in PEM format."""
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def get_public_jwk(self) -> dict[str, Any]:
        """Get public key in JWK format."""
        public_numbers = self.public_key.public_numbers()
        # Convert integers to base64url-encoded bytes
        import base64

        def int_to_base64url(n: int, length: int) -> str:
            data = n.to_bytes(length, byteorder="big")
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

        return {
            "kty": "RSA",
            "kid": self.kid,
            "use": "sig",
            "alg": "RS256",
            "n": int_to_base64url(public_numbers.n, 256),
            "e": int_to_base64url(public_numbers.e, 3),
        }


@pytest.fixture
def mock_key_pair() -> MockKeyPair:
    """Generate a mock RSA key pair for testing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return MockKeyPair(
        kid="test-key-1",
        private_key=private_key,
        public_key=private_key.public_key(),
    )


@pytest.fixture
def mock_jwks(mock_key_pair: MockKeyPair) -> dict[str, Any]:
    """Generate mock JWKS containing the test key."""
    return {"keys": [mock_key_pair.get_public_jwk()]}


@pytest.fixture
def token_claims() -> dict[str, Any]:
    """Standard token claims for testing."""
    now = int(time.time())
    return {
        "sub": "test-user-123",
        "email": "test@example.com",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_TestPool",
        "aud": "test-client-id",
        "iat": now,
        "exp": now + 3600,  # 1 hour from now
    }


@pytest.fixture
def valid_token(mock_key_pair: MockKeyPair, token_claims: dict[str, Any]) -> str:
    """Generate a valid JWT signed with the mock key."""
    return jwt.encode(
        token_claims,
        mock_key_pair.get_private_pem(),
        algorithm="RS256",
        headers={"kid": mock_key_pair.kid},
    )


@pytest.fixture
def expired_token(mock_key_pair: MockKeyPair, token_claims: dict[str, Any]) -> str:
    """Generate an expired JWT."""
    claims = token_claims.copy()
    claims["exp"] = int(time.time()) - 3600  # Expired 1 hour ago
    claims["iat"] = int(time.time()) - 7200  # Issued 2 hours ago
    return jwt.encode(
        claims,
        mock_key_pair.get_private_pem(),
        algorithm="RS256",
        headers={"kid": mock_key_pair.kid},
    )


@pytest.fixture
def token_missing_claims(mock_key_pair: MockKeyPair) -> str:
    """Generate a JWT missing required claims."""
    claims = {
        "sub": "test-user-123",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_TestPool",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        # Missing: email, aud
    }
    return jwt.encode(
        claims,
        mock_key_pair.get_private_pem(),
        algorithm="RS256",
        headers={"kid": mock_key_pair.kid},
    )


@pytest.fixture
def tampered_token(valid_token: str) -> str:
    """Create a token with tampered payload."""
    # Split the token and modify the payload
    parts = valid_token.split(".")
    # Tamper with the signature (change last character)
    tampered_sig = parts[2][:-1] + ("A" if parts[2][-1] != "A" else "B")
    return f"{parts[0]}.{parts[1]}.{tampered_sig}"


@pytest.fixture
def unknown_key_token(token_claims: dict[str, Any]) -> str:
    """Generate a token signed with an unknown key."""
    # Generate a different key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return jwt.encode(
        token_claims,
        private_pem,
        algorithm="RS256",
        headers={"kid": "unknown-key-id"},
    )


@pytest.fixture
def mock_cognito_settings() -> dict[str, str]:
    """Mock Cognito settings for testing."""
    return {
        "cognito_region": "us-east-1",
        "cognito_user_pool_id": "us-east-1_TestPool",
        "cognito_app_client_id": "test-client-id",
    }
