# Feature Specification: Bedrock Client

**Feature Branch**: `009-bedrock-client`  
**Created**: 2025-12-13  
**Status**: Draft  
**Depends On**: 034-environment-config

**Technical Context**: We use Bedrock Access Gateway (BAG) which provides an OpenAI-compatible API. This means we use OpenAI API format (`/v1/chat/completions`), NOT native Bedrock Converse API. BAG translates to Bedrock internally.

## User Scenarios & Testing

### User Story 1 - LLM Request (Priority: P1)

System can send chat completion requests to Bedrock.

**Why this priority**: Core LLM integration.

**Independent Test**: Send simple prompt, receive response.

**Acceptance Scenarios**:

1. **Given** valid conversation context, **When** request sent to Bedrock, **Then** response is returned
2. **Given** request with tools defined, **When** sent, **Then** Bedrock can return tool calls
3. **Given** invalid model ID, **When** request sent, **Then** error is returned with details

---

### User Story 2 - Model Configuration (Priority: P1)

System uses configured model for requests.

**Why this priority**: Need to specify which model to use.

**Independent Test**: Configure model A, verify requests use model A.

**Acceptance Scenarios**:

1. **Given** model configured in environment, **When** request made, **Then** configured model is used
2. **Given** model not configured, **When** application starts, **Then** default model is used

---

### User Story 3 - Request Formatting (Priority: P1)

Requests are formatted correctly for Bedrock API.

**Why this priority**: API compatibility required.

**Independent Test**: Build request, verify format matches Bedrock spec.

**Acceptance Scenarios**:

1. **Given** conversation messages, **When** request built, **Then** messages formatted per Bedrock API
2. **Given** tool definitions, **When** request built, **Then** tools formatted per Bedrock API

---

### Edge Cases

- What happens when Bedrock returns 429 (rate limit)? → Handled by 012-llm-error-handling
- What happens when model doesn't support tools? → Error surfaced to caller

## Requirements

### Functional Requirements

- **FR-001**: System MUST connect to BAG endpoint (`/api/v1/chat/completions`)
- **FR-002**: System MUST use OpenAI API format (messages array, model, tools)
- **FR-003**: System MUST include API key in Authorization header
- **FR-004**: System MUST format tool definitions per OpenAI function calling spec
- **FR-005**: System MUST include system prompt as first message with role "system"
- **FR-006**: System MUST set appropriate timeout (60s default)
- **FR-007**: System MUST request streaming via `stream: true`

### Configuration

| Variable | Description |
|----------|-------------|
| BAG_ENDPOINT | BAG URL (e.g., `http://bedrock-gateway:80/api/v1`) |
| BAG_API_KEY | API key for BAG authentication |
| BAG_MODEL | Model ID (e.g., `anthropic.claude-sonnet-4-20250514-v1:0`) |

### Key Entities

- **LLMClient**: HTTP client for BAG (OpenAI-compatible)
- **ChatRequest**: OpenAI format request (messages, model, tools, stream)
- **ChatResponse**: OpenAI format response (choices, usage)

## Success Criteria

- **SC-001**: Request formatting matches Bedrock API spec
- **SC-002**: Successful request/response round-trip
- **SC-003**: Model configuration is respected

