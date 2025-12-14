"""Secrets Manager integration for sensitive configuration.

This module provides optional integration with AWS Secrets Manager
for retrieving sensitive configuration values like database credentials.

Usage:
    manager = SecretsManager()
    secret = manager.get_secret("arn:aws:secretsmanager:...")

    # Or with fallback to environment variable:
    secret = manager.get_secret_or_env("arn:...", "DATABASE_URL")
"""

import os
import time
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)


def _create_secrets_client() -> Any:
    """Create boto3 Secrets Manager client."""
    import boto3

    return boto3.client("secretsmanager")


class SecretsManagerError(Exception):
    """Error fetching secret from Secrets Manager."""

    pass


class SecretsManager:
    """Client wrapper for AWS Secrets Manager with retry logic."""

    def __init__(self, max_retries: int = 1, retry_delay: float = 0.5) -> None:
        """Initialize the Secrets Manager client.

        Args:
            max_retries: Maximum number of retry attempts (default: 1).
            retry_delay: Delay between retries in seconds (default: 0.5).
        """
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._client = None

    def _get_client(self) -> Any:
        """Lazily initialize boto3 client."""
        if self._client is None:
            self._client = _create_secrets_client()
        return self._client

    def get_secret(self, secret_arn: str) -> str:
        """Fetch a secret value from Secrets Manager.

        Args:
            secret_arn: ARN or name of the secret.

        Returns:
            The secret value as a string.

        Raises:
            SecretsManagerError: If the secret cannot be fetched after retries.
        """
        client = self._get_client()
        last_error = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.get_secret_value(SecretId=secret_arn)

                # Handle string or binary secret
                if "SecretString" in response:
                    return response["SecretString"]
                if "SecretBinary" in response:
                    return response["SecretBinary"].decode("utf-8")

                msg = f"Secret {secret_arn} has no value"
                raise SecretsManagerError(msg)

            except SecretsManagerError:
                raise
            except Exception as e:
                last_error = e
                logger.warning(
                    "secrets_manager_error",
                    secret_arn=secret_arn,
                    attempt=attempt + 1,
                    max_retries=self._max_retries,
                    error=str(e),
                )

                if attempt < self._max_retries:
                    time.sleep(self._retry_delay)

        msg = f"Failed to fetch secret {secret_arn} after {self._max_retries + 1} attempts: {last_error}"
        raise SecretsManagerError(msg)

    def get_secret_or_env(self, secret_arn: str, env_var: str) -> str:
        """Fetch a secret, falling back to environment variable.

        Args:
            secret_arn: ARN or name of the secret.
            env_var: Environment variable name for fallback.

        Returns:
            The secret value (from Secrets Manager or env var).

        Raises:
            SecretsManagerError: If both sources fail.
        """
        try:
            return self.get_secret(secret_arn)
        except SecretsManagerError:
            logger.info(
                "secrets_manager_fallback",
                secret_arn=secret_arn,
                env_var=env_var,
            )

            value = os.environ.get(env_var)
            if value is not None:
                return value

            msg = f"Failed to fetch secret and no fallback env var {env_var}"
            raise SecretsManagerError(msg) from None
