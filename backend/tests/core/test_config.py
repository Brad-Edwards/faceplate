"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import (
    BedrockSettings,
    CognitoSettings,
    clear_settings_cache,
    get_settings,
)

# =============================================================================
# User Story 1: Environment Variables Tests
# =============================================================================


class TestEnvironmentVariables:
    """Tests for loading config from environment variables."""

    def test_loads_from_env(self, full_env: dict[str, str]) -> None:
        """T005: Config loads values from environment variables."""
        clear_settings_cache()
        settings = get_settings()

        assert settings.database_url.get_secret_value() == full_env["DATABASE_URL"]
        assert settings.cognito.cognito_region == full_env["COGNITO_REGION"]
        assert settings.cognito.cognito_user_pool_id == full_env["COGNITO_USER_POOL_ID"]
        assert settings.bedrock.bedrock_endpoint == full_env["BEDROCK_ENDPOINT"]
        assert settings.log_level == full_env["LOG_LEVEL"]
        assert settings.max_tool_calls == int(full_env["MAX_TOOL_CALLS"])

    def test_defaults(self, minimal_env: dict[str, str]) -> None:
        """T006: Optional vars use defaults when not set."""
        clear_settings_cache()
        settings = get_settings()

        # Check defaults are applied
        assert settings.cognito.cognito_region == "us-east-1"
        assert settings.bedrock.bedrock_model == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert settings.bedrock.bedrock_max_tokens == 4096
        assert settings.log_level == "INFO"
        assert settings.max_tool_calls == 20
        assert settings.jwks_cache_ttl == 3600

    def test_invalid_value(self, minimal_env: dict[str, str]) -> None:
        """T007: Invalid values raise validation error."""
        clear_settings_cache()

        with patch.dict(os.environ, {"MAX_TOOL_CALLS": "-5"}), pytest.raises(ValidationError, match=r"max_tool_calls"):
            clear_settings_cache()
            get_settings()

    def test_invalid_log_level(self, minimal_env: dict[str, str]) -> None:
        """Test invalid log level raises error."""
        clear_settings_cache()

        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}), pytest.raises(ValidationError, match=r"log_level"):
            clear_settings_cache()
            get_settings()


# =============================================================================
# User Story 2: Required vs Optional Tests
# =============================================================================


class TestRequiredOptional:
    """Tests for required vs optional configuration."""

    def test_required_missing_fails(self, clean_env: None) -> None:
        """T011: Missing required var fails with clear message."""
        clear_settings_cache()

        # No required vars set
        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        # Check error mentions missing field
        error_str = str(exc_info.value)
        assert "database_url" in error_str.lower() or "field required" in error_str.lower()

    def test_required_present_succeeds(self, minimal_env: dict[str, str]) -> None:
        """T012: All required vars present allows startup."""
        clear_settings_cache()
        settings = get_settings()

        assert settings.database_url.get_secret_value() == minimal_env["DATABASE_URL"]
        assert settings.cognito.cognito_user_pool_id == minimal_env["COGNITO_USER_POOL_ID"]
        assert settings.cognito.cognito_app_client_id == minimal_env["COGNITO_APP_CLIENT_ID"]

    def test_error_message(self, clean_env: None) -> None:
        """T013: Error message is descriptive."""
        clear_settings_cache()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        # Pydantic errors include field names
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Each error should have a 'loc' with field name
        for error in errors:
            assert "loc" in error
            assert len(error["loc"]) > 0

    def test_cognito_required_fields(self, clean_env: None) -> None:
        """Test that Cognito required fields cause failure."""
        clear_settings_cache()

        # Only set database_url, missing Cognito fields
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/testdb"},
        ):
            with pytest.raises(ValidationError) as exc_info:
                clear_settings_cache()
                get_settings()

            error_str = str(exc_info.value)
            assert "cognito" in error_str.lower() or "user_pool_id" in error_str.lower()


# =============================================================================
# Additional Validation Tests
# =============================================================================


class TestValidation:
    """Additional validation tests."""

    def test_bedrock_max_tokens_positive(self) -> None:
        """Test bedrock_max_tokens must be positive."""
        with pytest.raises(ValidationError, match=r"positive"):
            BedrockSettings(bedrock_max_tokens=0)

    def test_jwks_cache_ttl_positive(self, minimal_env: dict[str, str]) -> None:
        """Test jwks_cache_ttl must be positive."""
        clear_settings_cache()

        with patch.dict(os.environ, {"JWKS_CACHE_TTL": "0"}), pytest.raises(ValidationError, match=r"positive"):
            clear_settings_cache()
            get_settings()

    def test_cognito_computed_properties(self) -> None:
        """Test Cognito computed properties."""
        settings = CognitoSettings(
            cognito_region="us-west-2",
            cognito_user_pool_id="us-west-2_TestPool",
            cognito_app_client_id="test-client",
        )

        assert "us-west-2" in settings.jwks_url
        assert "us-west-2_TestPool" in settings.jwks_url
        assert ".well-known/jwks.json" in settings.jwks_url

        assert "us-west-2" in settings.issuer
        assert "us-west-2_TestPool" in settings.issuer

    def test_settings_caching(self, minimal_env: dict[str, str]) -> None:
        """Test that settings are cached."""
        clear_settings_cache()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_clear_cache(self, minimal_env: dict[str, str]) -> None:
        """Test cache clearing works."""
        clear_settings_cache()
        settings1 = get_settings()

        clear_settings_cache()
        settings2 = get_settings()

        # Different instances after cache clear
        assert settings1 is not settings2

    def test_secret_str_not_exposed(self, minimal_env: dict[str, str]) -> None:
        """Test that SecretStr values are not exposed in repr."""
        clear_settings_cache()
        settings = get_settings()

        # SecretStr should be masked in repr
        repr_str = repr(settings)
        assert "postgresql+asyncpg://" not in repr_str
        assert "**********" in repr_str or "SecretStr" in repr_str
