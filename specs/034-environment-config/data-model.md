# Data Model: Environment Config

**Feature**: 034-environment-config  
**Date**: 2025-12-14

## Overview

Environment configuration has no database entities. All configuration is runtime state loaded at application startup.

## Configuration Classes

### Settings (Root)

Main application settings container.

```
Settings
├── database_url: SecretStr       # Required - PostgreSQL connection
├── log_level: str                # Optional - default: INFO
├── max_tool_calls: int           # Optional - default: 20
├── jwks_cache_ttl: int           # Optional - default: 3600
├── cognito: CognitoSettings      # Nested - Cognito configuration
└── bedrock: BedrockSettings      # Nested - Bedrock configuration
```

### CognitoSettings

AWS Cognito authentication configuration.

```
CognitoSettings
├── region: str                   # Optional - default: us-east-1
├── user_pool_id: str             # Required
├── app_client_id: str            # Required
├── jwks_url: str                 # Computed property
└── issuer: str                   # Computed property
```

### BedrockSettings

AWS Bedrock LLM configuration.

```
BedrockSettings
├── endpoint: str                 # Optional - BAG endpoint URL
├── model: str                    # Optional - default model ID
└── max_tokens: int               # Optional - default: 4096
```

## Validation Rules

| Field | Validation |
|-------|------------|
| database_url | Must be valid PostgreSQL URL |
| log_level | Must be DEBUG, INFO, WARNING, ERROR |
| max_tool_calls | Must be positive integer |
| cognito.user_pool_id | Must match pattern `{region}_{id}` |

## Database Impact

None. This spec does not modify the database schema.

## Relationship to Other Specs

- **002-jwt-validation**: Uses CognitoSettings for JWT validation
- **009-bedrock-client**: Uses BedrockSettings for LLM calls
- **001-database-schema**: Uses database_url for connection

