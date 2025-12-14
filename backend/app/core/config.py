"""Application configuration.

This module provides centralized configuration management using pydantic-settings.
All configuration is loaded from environment variables at startup.

Required environment variables:
- DATABASE_URL: PostgreSQL connection string
- COGNITO_USER_POOL_ID: AWS Cognito user pool ID
- COGNITO_APP_CLIENT_ID: AWS Cognito app client ID

Optional environment variables (with defaults):
- COGNITO_REGION: AWS region (default: us-east-1)
- BEDROCK_ENDPOINT: Bedrock Access Gateway URL (default: empty)
- BEDROCK_MODEL: Default model ID (default: anthropic.claude-3-5-sonnet-20241022-v2:0)
- BEDROCK_MAX_TOKENS: Max tokens per response (default: 4096)
- LOG_LEVEL: Logging level (default: INFO)
- MAX_TOOL_CALLS: Max tool calls per agent turn (default: 20)
- JWKS_CACHE_TTL: JWKS cache TTL in seconds (default: 3600)
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings


class CognitoSettings(BaseSettings):
    """AWS Cognito configuration."""

    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str  # Required - no default
    cognito_app_client_id: str  # Required - no default

    @property
    def jwks_url(self) -> str:
        """JWKS endpoint URL for the Cognito user pool."""
        return (
            f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}/.well-known/jwks.json"
        )

    @property
    def issuer(self) -> str:
        """Expected token issuer URL."""
        return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}"

    model_config = {"env_prefix": "", "case_sensitive": False}


class BedrockSettings(BaseSettings):
    """AWS Bedrock configuration for LLM access."""

    bedrock_endpoint: str = ""  # Optional - BAG URL
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_max_tokens: int = 4096

    @field_validator("bedrock_max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max_tokens is positive."""
        if v <= 0:
            msg = "bedrock_max_tokens must be positive"
            raise ValueError(msg)
        return v

    model_config = {"env_prefix": "", "case_sensitive": False}


class Settings(BaseSettings):
    """Application settings.

    Required fields will cause a ValidationError if not set in the environment.
    Optional fields have sensible defaults.
    """

    # Database (required)
    database_url: SecretStr  # Required - no default, sensitive

    # Cognito (nested, has its own required fields)
    cognito: CognitoSettings = None  # type: ignore[assignment]

    # Bedrock (nested, all optional)
    bedrock: BedrockSettings = None  # type: ignore[assignment]

    # Application settings (optional)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_tool_calls: int = 20
    jwks_cache_ttl: int = 3600  # 1 hour in seconds

    def __init__(self, **data):
        """Initialize settings with nested models."""
        # Initialize nested settings from environment
        if "cognito" not in data or data["cognito"] is None:
            data["cognito"] = CognitoSettings()
        if "bedrock" not in data or data["bedrock"] is None:
            data["bedrock"] = BedrockSettings()
        super().__init__(**data)

    @field_validator("max_tool_calls")
    @classmethod
    def validate_max_tool_calls(cls, v: int) -> int:
        """Validate max_tool_calls is positive."""
        if v <= 0:
            msg = "max_tool_calls must be positive"
            raise ValueError(msg)
        return v

    @field_validator("jwks_cache_ttl")
    @classmethod
    def validate_jwks_cache_ttl(cls, v: int) -> int:
        """Validate jwks_cache_ttl is positive."""
        if v <= 0:
            msg = "jwks_cache_ttl must be positive"
            raise ValueError(msg)
        return v

    model_config = {"env_prefix": "", "case_sensitive": False, "env_nested_delimiter": "__"}


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Cached Settings instance loaded from environment.

    Raises:
        ValidationError: If required environment variables are missing.
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache. Useful for testing."""
    get_settings.cache_clear()
