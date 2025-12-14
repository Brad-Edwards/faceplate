"""Test fixtures for configuration testing."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Fixture that clears config-related environment variables."""
    env_vars = [
        "DATABASE_URL",
        "COGNITO_REGION",
        "COGNITO_USER_POOL_ID",
        "COGNITO_APP_CLIENT_ID",
        "BEDROCK_ENDPOINT",
        "BEDROCK_MODEL",
        "BEDROCK_MAX_TOKENS",
        "LOG_LEVEL",
        "MAX_TOOL_CALLS",
        "JWKS_CACHE_TTL",
    ]
    # Save original values
    original = {k: os.environ.get(k) for k in env_vars}

    # Clear all
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def minimal_env(clean_env: None) -> Generator[dict[str, str], None, None]:
    """Fixture with minimum required environment variables."""
    env = {
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/testdb",
        "COGNITO_USER_POOL_ID": "us-east-1_TestPool",
        "COGNITO_APP_CLIENT_ID": "test-client-id",
    }
    with patch.dict(os.environ, env):
        yield env


@pytest.fixture
def full_env(clean_env: None) -> Generator[dict[str, str], None, None]:
    """Fixture with all environment variables set."""
    env = {
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/testdb",
        "COGNITO_REGION": "us-west-2",
        "COGNITO_USER_POOL_ID": "us-west-2_FullPool",
        "COGNITO_APP_CLIENT_ID": "full-client-id",
        "BEDROCK_ENDPOINT": "http://localhost:8080",
        "BEDROCK_MODEL": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "BEDROCK_MAX_TOKENS": "8192",
        "LOG_LEVEL": "DEBUG",
        "MAX_TOOL_CALLS": "50",
        "JWKS_CACHE_TTL": "7200",
    }
    with patch.dict(os.environ, env):
        yield env
