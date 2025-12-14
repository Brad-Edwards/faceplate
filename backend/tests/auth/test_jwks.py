"""Tests for JWKS caching."""

import time
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.auth.exceptions import JWKSFetchError, KeyNotFoundError
from app.auth.jwks import JWKSCache
from app.core.config import CognitoSettings

from .conftest import MockKeyPair


class TestJWKSCache:
    """Tests for JWKS caching functionality."""

    @pytest.fixture
    def cognito_settings(self, mock_cognito_settings: dict[str, str]) -> CognitoSettings:
        """Create CognitoSettings from mock values."""
        return CognitoSettings(**mock_cognito_settings)

    @pytest.fixture
    def cache(self, cognito_settings: CognitoSettings) -> JWKSCache:
        """Create a JWKSCache instance."""
        return JWKSCache(cognito_settings, ttl=3600)

    def _create_mock_response(self, mock_jwks: dict[str, Any]) -> MagicMock:
        """Create a mock httpx response."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_jwks
        mock_response.raise_for_status.return_value = None
        return mock_response

    async def test_keys_fetched_on_first_call(
        self,
        cache: JWKSCache,
        mock_jwks: dict[str, Any],
        mock_key_pair: MockKeyPair,
    ) -> None:
        """T021: Keys are fetched from IdP on first call."""
        mock_response = self._create_mock_response(mock_jwks)

        async def mock_get(*args, **kwargs):
            return mock_response

        with patch.object(cache._client, "get", side_effect=mock_get) as mock_get_method:
            key = await cache.get_key(mock_key_pair.kid)

            # Verify fetch was called
            mock_get_method.assert_called_once()
            # Verify key was returned
            assert key is not None
            assert key["kid"] == mock_key_pair.kid

    async def test_cached_keys_used(
        self,
        cache: JWKSCache,
        mock_jwks: dict[str, Any],
        mock_key_pair: MockKeyPair,
    ) -> None:
        """T022: Cached keys are used within TTL (no network call)."""
        mock_response = self._create_mock_response(mock_jwks)
        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch.object(cache._client, "get", side_effect=mock_get):
            # First call - should fetch
            await cache.get_key(mock_key_pair.kid)
            assert call_count == 1

            # Second call - should use cache
            await cache.get_key(mock_key_pair.kid)
            assert call_count == 1  # Still 1, no new fetch

    async def test_keys_refresh_after_ttl(
        self,
        cognito_settings: CognitoSettings,
        mock_jwks: dict[str, Any],
        mock_key_pair: MockKeyPair,
    ) -> None:
        """T023: Keys are refreshed after TTL expires."""
        # Create cache with very short TTL
        cache = JWKSCache(cognito_settings, ttl=1)
        mock_response = MagicMock()
        mock_response.json.return_value = mock_jwks
        mock_response.raise_for_status.return_value = None
        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch.object(cache._client, "get", side_effect=mock_get):
            # First call
            await cache.get_key(mock_key_pair.kid)
            assert call_count == 1

            # Simulate TTL expiration
            cache._cache_timestamp = time.time() - 2

            # Second call after TTL - should refetch
            await cache.get_key(mock_key_pair.kid)
            assert call_count == 2

    async def test_idp_down_uses_cache(
        self,
        cache: JWKSCache,
        mock_jwks: dict[str, Any],
        mock_key_pair: MockKeyPair,
    ) -> None:
        """T024: When IdP is down, use cached keys if still valid."""
        mock_response = self._create_mock_response(mock_jwks)
        call_count = 0
        should_fail = False

        async def mock_get(*args, **kwargs):
            nonlocal call_count, should_fail
            call_count += 1
            if should_fail:
                raise httpx.HTTPError("Connection failed")
            return mock_response

        with patch.object(cache._client, "get", side_effect=mock_get):
            # First call - populate cache
            await cache.get_key(mock_key_pair.kid)
            assert call_count == 1

            # Simulate IdP failure on next request
            should_fail = True

            # Force refresh attempt by expiring cache
            cache._cache_timestamp = time.time() - cache._ttl - 1

            # Should still return cached key (graceful degradation)
            key = await cache.get_key(mock_key_pair.kid)
            assert key is not None
            assert key["kid"] == mock_key_pair.kid

    async def test_key_not_found_raises(
        self,
        cache: JWKSCache,
        mock_jwks: dict[str, Any],
    ) -> None:
        """Test that KeyNotFoundError is raised for unknown key IDs."""
        mock_response = self._create_mock_response(mock_jwks)

        async def mock_get(*args, **kwargs):
            return mock_response

        with patch.object(cache._client, "get", side_effect=mock_get), pytest.raises(KeyNotFoundError):
            await cache.get_key("non-existent-kid")

    async def test_fetch_error_no_cache(
        self,
        cache: JWKSCache,
    ) -> None:
        """Test that JWKSFetchError is raised when fetch fails and no cache."""

        async def mock_get(*args, **kwargs):
            raise httpx.HTTPError("Connection failed")

        with patch.object(cache._client, "get", side_effect=mock_get), pytest.raises(JWKSFetchError):
            await cache.get_key("any-kid")

    async def test_refresh_method(
        self,
        cache: JWKSCache,
        mock_jwks: dict[str, Any],
    ) -> None:
        """Test explicit refresh method."""
        mock_response = self._create_mock_response(mock_jwks)

        async def mock_get(*args, **kwargs):
            return mock_response

        with patch.object(cache._client, "get", side_effect=mock_get) as mock_get_method:
            await cache.refresh()

            mock_get_method.assert_called_once()
            assert cache._keys is not None
