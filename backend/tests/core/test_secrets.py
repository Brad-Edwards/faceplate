"""Tests for Secrets Manager integration."""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.secrets import SecretsManager, SecretsManagerError


class TestSecretsManager:
    """Tests for SecretsManager class."""

    @pytest.fixture
    def mock_boto_client(self) -> MagicMock:
        """Create a mock boto3 Secrets Manager client."""
        return MagicMock()

    @pytest.fixture
    def manager(self) -> SecretsManager:
        """Create a SecretsManager instance."""
        return SecretsManager(max_retries=1, retry_delay=0.01)

    def test_fetch_secret(self, manager: SecretsManager, mock_boto_client: MagicMock) -> None:
        """T016: Test secrets manager fetches secret successfully."""
        mock_boto_client.get_secret_value.return_value = {"SecretString": "my-secret-value"}

        with patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client):
            result = manager.get_secret("arn:aws:secretsmanager:us-east-1:123456:secret:test")

        assert result == "my-secret-value"
        mock_boto_client.get_secret_value.assert_called_once()

    def test_fetch_binary_secret(self, manager: SecretsManager, mock_boto_client: MagicMock) -> None:
        """Test fetching binary secret."""
        mock_boto_client.get_secret_value.return_value = {"SecretBinary": b"binary-secret"}

        with patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client):
            result = manager.get_secret("arn:aws:secretsmanager:us-east-1:123456:secret:test")

        assert result == "binary-secret"

    def test_fallback_to_env(self, manager: SecretsManager, mock_boto_client: MagicMock) -> None:
        """T017: Test fallback to environment variable when Secrets Manager fails."""
        mock_boto_client.get_secret_value.side_effect = Exception("Access denied")

        with (
            patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client),
            patch.dict(os.environ, {"TEST_VAR": "env-value"}),
        ):
            result = manager.get_secret_or_env(
                "arn:aws:secretsmanager:us-east-1:123456:secret:test",
                "TEST_VAR",
            )

        assert result == "env-value"

    def test_timeout_retry(self, mock_boto_client: MagicMock) -> None:
        """T018: Test retry behavior on transient failures."""
        manager = SecretsManager(max_retries=2, retry_delay=0.01)

        # First two calls fail, third succeeds
        mock_boto_client.get_secret_value.side_effect = [
            Exception("Timeout"),
            Exception("Timeout"),
            {"SecretString": "success"},
        ]

        with patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client):
            result = manager.get_secret("arn:aws:secretsmanager:us-east-1:123456:secret:test")

        assert result == "success"
        assert mock_boto_client.get_secret_value.call_count == 3

    def test_max_retries_exceeded(self, mock_boto_client: MagicMock) -> None:
        """Test that error is raised after max retries."""
        manager = SecretsManager(max_retries=1, retry_delay=0.01)

        mock_boto_client.get_secret_value.side_effect = Exception("Connection failed")

        with (
            patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client),
            pytest.raises(SecretsManagerError, match=r"Failed to fetch"),
        ):
            manager.get_secret("arn:aws:secretsmanager:us-east-1:123456:secret:test")

        # Should have tried max_retries + 1 times
        assert mock_boto_client.get_secret_value.call_count == 2

    def test_no_value_raises(self, manager: SecretsManager, mock_boto_client: MagicMock) -> None:
        """Test that empty response raises error."""
        mock_boto_client.get_secret_value.return_value = {}

        with (
            patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client),
            pytest.raises(SecretsManagerError, match=r"no value"),
        ):
            manager.get_secret("arn:aws:secretsmanager:us-east-1:123456:secret:test")

    def test_fallback_no_env_raises(self, manager: SecretsManager, mock_boto_client: MagicMock) -> None:
        """Test that missing env var after failed fetch raises error."""
        mock_boto_client.get_secret_value.side_effect = Exception("Access denied")

        with (
            patch("app.core.secrets._create_secrets_client", return_value=mock_boto_client),
            pytest.raises(SecretsManagerError, match=r"no fallback"),
        ):
            manager.get_secret_or_env(
                "arn:aws:secretsmanager:us-east-1:123456:secret:test",
                "NONEXISTENT_VAR",
            )

    def test_lazy_client_initialization(self, manager: SecretsManager) -> None:
        """Test that boto client is initialized lazily."""
        assert manager._client is None

        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {"SecretString": "test"}

        with patch("app.core.secrets._create_secrets_client", return_value=mock_client):
            manager.get_secret("test-secret")

        # Client should now be set
        assert manager._client is not None
