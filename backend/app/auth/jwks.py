"""JWKS caching for Cognito public keys."""

import time
from typing import Any

import httpx
import structlog

from app.core.config import CognitoSettings

from .exceptions import JWKSFetchError, KeyNotFoundError

logger = structlog.get_logger(__name__)


class JWKSCache:
    """Caches JWKS from Cognito with TTL-based expiration."""

    def __init__(self, settings: CognitoSettings, ttl: int = 3600) -> None:
        """Initialize the JWKS cache.

        Args:
            settings: Cognito configuration.
            ttl: Cache time-to-live in seconds (default: 1 hour).
        """
        self._settings = settings
        self._ttl = ttl
        self._keys: dict[str, dict[str, Any]] = {}
        self._cache_timestamp: float = 0
        self._client = httpx.AsyncClient(timeout=10.0)

    async def get_key(self, kid: str) -> dict[str, Any]:
        """Get a public key by key ID.

        Args:
            kid: Key ID from JWT header.

        Returns:
            JWK dict for the requested key.

        Raises:
            KeyNotFoundError: Key ID not found in JWKS.
            JWKSFetchError: Failed to fetch JWKS and no cached keys.
        """
        # Check if cache is expired or empty
        if self._is_cache_expired():
            await self._refresh_keys()

        if kid not in self._keys:
            logger.warning("key_not_found", kid=kid, available_kids=list(self._keys.keys()))
            raise KeyNotFoundError(kid)

        return self._keys[kid]

    async def refresh(self) -> None:
        """Force a cache refresh from the JWKS endpoint.

        Raises:
            JWKSFetchError: Failed to fetch JWKS.
        """
        await self._refresh_keys(force=True)

    def _is_cache_expired(self) -> bool:
        """Check if the cache has expired."""
        if not self._keys:
            return True
        return time.time() - self._cache_timestamp > self._ttl

    async def _refresh_keys(self, force: bool = False) -> None:
        """Refresh keys from the JWKS endpoint.

        Args:
            force: If True, raise on failure. If False, use stale cache on failure.

        Raises:
            JWKSFetchError: Failed to fetch and no cached keys available.
        """
        try:
            response = await self._client.get(self._settings.jwks_url)
            response.raise_for_status()

            jwks = response.json()
            self._update_cache(jwks)

            logger.info(
                "jwks_refreshed",
                key_count=len(self._keys),
                ttl=self._ttl,
            )

        except httpx.HTTPError as e:
            logger.warning("jwks_fetch_failed", error=str(e), url=self._settings.jwks_url)

            # If we have cached keys, use them (graceful degradation)
            if self._keys and not force:
                logger.info("using_stale_cache", key_count=len(self._keys))
                return

            raise JWKSFetchError(f"Failed to fetch JWKS: {e}") from e

    def _update_cache(self, jwks: dict[str, Any]) -> None:
        """Update the cache with new JWKS data.

        Args:
            jwks: JWKS response with keys array.
        """
        self._keys = {}
        for key in jwks.get("keys", []):
            kid = key.get("kid")
            if kid:
                self._keys[kid] = key

        self._cache_timestamp = time.time()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
