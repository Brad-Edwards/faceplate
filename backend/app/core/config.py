"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class CognitoSettings(BaseSettings):
    """AWS Cognito configuration."""

    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str = ""
    cognito_app_client_id: str = ""

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


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/faceplate"

    # Cognito
    cognito: CognitoSettings = CognitoSettings()

    # JWKS Cache
    jwks_cache_ttl: int = 3600  # 1 hour in seconds

    model_config = {"env_prefix": "", "case_sensitive": False, "env_nested_delimiter": "__"}


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
