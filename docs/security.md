# Security

Security controls and threat model for Faceplate.

## Threat Model

### Assets

- User conversations (potentially containing sensitive attack methodologies)
- MCP SSH keys (access to range machines)
- JWT tokens (user authentication)
- Range configurations (IP addresses, credentials)

### Threats

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Unauthorized access to chat history | High | Cognito JWT validation, per-user conversations |
| MCP SSH key exposure | Critical | Secrets Manager encryption, IAM policies |
| WebSocket hijacking | High | JWT validation on connect, TLS encryption |
| SQL injection | High | SQLAlchemy ORM, parameterized queries |
| Cross-range access | Critical | Range ID validation, security group isolation |
| Excessive tool calls (DoS) | Medium | Rate limiting, max tool call limits |
| LLM prompt injection | Medium | System prompt isolation, tool validation |

## Authentication

### JWT Validation

**Flow:**
1. Frontend receives JWT from Portal (Cognito OIDC)
2. JWT stored in httpOnly cookie
3. WebSocket connection includes JWT in Authorization header
4. Backend validates JWT signature against Cognito public keys
5. User email extracted from claims for authorization

**Implementation:**
```python
# app/auth.py

async def validate_token(token: str) -> Dict:
    # Fetch Cognito public keys (cached)
    public_keys = await get_cognito_public_keys()
    
    # Decode header to get kid
    header = jwt.get_unverified_header(token)
    
    # Find matching key
    key = next(k for k in public_keys["keys"] if k["kid"] == header["kid"])
    
    # Verify signature and claims
    claims = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        audience=settings.cognito_client_id,
        issuer=f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"
    )
    
    # Verify token not expired
    if claims["exp"] < time.time():
        raise HTTPException(401, "Token expired")
    
    return claims
```

**Security Controls:**
- RS256 asymmetric signature validation
- Audience and issuer claim verification
- Expiration time check
- Public keys cached with 1-hour refresh
- WebSocket closed immediately on auth failure

### Authorization

**Conversation Access:**
```python
# Only load conversations owned by authenticated user
conversations = db.query(Conversation).filter(
    Conversation.user_email == current_user["email"]
).all()
```

**Range Access:**
```python
# Verify user owns the range before loading MCP config
range = db.query(Range).filter(
    Range.id == range_id,
    Range.user_email == current_user["email"],
    Range.status == "active"
).first()

if not range:
    raise HTTPException(403, "Access denied")
```

**MCP Tool Execution:**
```python
# MCP config is loaded per-range, ensuring tools only execute on user's machines
mcp_manager = MCPManager(range_id=user_active_range_id)
```

## Network Security

### VPC Isolation

```
┌─────────────────────────────────────────┐
│ Portal VPC (10.0.0.0/16)                │
│                                         │
│ ┌─────────────┐     ┌─────────────┐   │
│ │ Public      │     │ Private     │   │
│ │             │     │             │   │
│ │ ALB         │────▶│ Faceplate   │   │
│ │             │     │ EC2         │   │
│ └─────────────┘     └──────┬──────┘   │
│                            │           │
│                     ┌──────▼──────┐   │
│                     │ PostgreSQL  │   │
│                     │ RDS         │   │
│                     └─────────────┘   │
└─────────────────────────────────────────┘
         │
         │ SSH (MCP)
         │
         ▼
┌─────────────────────────────────────────┐
│ Range VPC (10.1.0.0/16)                 │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ User Subnet A (/24)               │  │
│ │  Kali ◀─────▶ Victim              │  │
│ └───────────────────────────────────┘  │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ User Subnet B (/24)               │  │
│ │  Kali ◀─────▶ Victim              │  │
│ └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Security Controls:**
- Faceplate in private subnet (no direct internet access)
- Inbound traffic only from ALB (security group)
- Outbound to RDS, NAT, and Range VPC (SSH)
- No VPC peering (SSH over internet gateway with key auth)

### Security Groups

**Faceplate EC2:**
```hcl
# Ingress: ALB only
ingress {
  from_port       = 8000
  to_port         = 8000
  protocol        = "tcp"
  security_groups = [alb_security_group_id]
}

# Egress: RDS
egress {
  from_port       = 5432
  to_port         = 5432
  protocol        = "tcp"
  security_groups = [rds_security_group_id]
}

# Egress: NAT (Cognito, Bedrock, MCP)
egress {
  from_port   = 0
  to_port     = 0
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]
}
```

**Range Instances (Kali/Victim):**
```hcl
# SSH from Portal VPC CIDR only
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/16"]  # Portal VPC
}
```

**Cross-Range Isolation:**
- Security groups reference specific SG IDs, not CIDR blocks
- Kali in Subnet A cannot access Victim in Subnet B
- Each user's machines isolated to their /24 subnet

## Data Protection

### Encryption in Transit

**HTTPS (ALB → Browser):**
- TLS 1.3 enforced
- ACM certificate with automatic rotation
- HTTP redirects to HTTPS

**WebSocket (Backend → Browser):**
- WSS (WebSocket Secure) over TLS
- Same TLS certificate as HTTP

**Database (Backend → RDS):**
- TLS 1.2+ enforced on RDS connection
- Certificate validation enabled

**SSH (Backend → Range):**
- SSH keys (4096-bit RSA or ed25519)
- No password authentication
- HostKeyChecking=accept-new (Range VPC is isolated)

### Encryption at Rest

**RDS:**
- Storage encryption enabled (AWS managed key)
- Automated backups encrypted
- No unencrypted snapshots

**Secrets Manager:**
- AES-256 encryption
- Per-secret KMS keys (future: CMK)

**ECR:**
- Image encryption at rest (AES-256)

**S3 (SSH keys):**
- Server-side encryption (SSE-S3)
- Future: SSE-KMS with CMK

### Secrets Management

**Storage:**
```
AWS Secrets Manager:
├── faceplate/dev/db-credentials
├── faceplate/prod/db-credentials
└── faceplate/ssh-keys/{range_id}

Environment Variables (EC2):
├── DATABASE_URL (from Secrets Manager)
├── COGNITO_USER_POOL_ID
├── COGNITO_CLIENT_ID
├── BEDROCK_ENDPOINT
└── MCP_KEY_BUCKET
```

**Access Control:**
```json
{
  "Effect": "Allow",
  "Action": ["secretsmanager:GetSecretValue"],
  "Resource": [
    "arn:aws:secretsmanager:*:*:secret:faceplate/*"
  ],
  "Condition": {
    "StringEquals": {
      "aws:PrincipalTag/Component": "faceplate"
    }
  }
}
```

**Rotation:**
- Database credentials: Manual rotation (future: automatic)
- SSH keys: Generated per-range, destroyed with range
- JWT signing keys: Managed by Cognito (automatic rotation)

## Input Validation

### User Messages

**Backend validation:**
```python
# Maximum message length
if len(message) > 10000:
    raise ValueError("Message too long")

# Sanitize for logging (no PII)
logged_message = message[:100] + "..." if len(message) > 100 else message
logger.info(f"User message: {logged_message}")
```

**No HTML sanitization needed:**
- Messages stored as plain text
- Frontend renders as text (no XSS risk)

### Tool Arguments

**MCP tool validation:**
```python
# Validate tool exists
if tool_name not in available_tools:
    raise ValueError(f"Unknown tool: {tool_name}")

# Validate arguments match tool schema
tool_schema = available_tools[tool_name]["parameters"]
validate_json_schema(arguments, tool_schema)

# Additional validation for dangerous operations
if tool_name.endswith("_execute_command"):
    # No command injection via shell metacharacters
    if any(char in arguments["command"] for char in [";", "|", "&", "$"]):
        # Allow these but log for monitoring
        logger.warning(f"Shell metacharacters in command: {arguments['command']}")
```

### Database Queries

**SQLAlchemy ORM:**
```python
# Parameterized queries (no SQL injection)
conversation = db.query(Conversation).filter(
    Conversation.id == conversation_id,  # Parameterized
    Conversation.user_email == user_email  # Parameterized
).first()

# Never use raw SQL with f-strings
# BAD: db.execute(f"SELECT * FROM conversations WHERE id = '{conv_id}'")
# GOOD: db.execute("SELECT * FROM conversations WHERE id = :id", {"id": conv_id})
```

## Rate Limiting

### Agent Loop Limits

**Per-conversation turn:**
```python
MAX_TOOL_CALLS = 20  # Total tools per user message
MAX_CONSECUTIVE_TOOLS = 10  # Without LLM text response
```

**Implementation:**
```python
class AgentOrchestrator:
    def __init__(self):
        self.tool_call_count = 0
        self.consecutive_tool_count = 0
    
    async def _agent_loop(self):
        while self.tool_call_count < MAX_TOOL_CALLS:
            response = await self._call_bedrock()
            
            if response["type"] == "tool_call":
                self.tool_call_count += 1
                self.consecutive_tool_count += 1
                
                if self.consecutive_tool_count >= MAX_CONSECUTIVE_TOOLS:
                    raise AgentError("Too many consecutive tool calls")
            
            elif response["type"] == "content":
                self.consecutive_tool_count = 0  # Reset
```

### User Rate Limiting (Future)

**Per-user limits:**
- 100 messages per hour
- 1000 tool calls per day
- 10 active conversations max

**Implementation:**
```python
# Redis-based rate limiting
from redis import Redis
from datetime import timedelta

redis = Redis()

def check_rate_limit(user_email: str, limit: int, window: timedelta):
    key = f"rate_limit:{user_email}:{window}"
    count = redis.incr(key)
    
    if count == 1:
        redis.expire(key, int(window.total_seconds()))
    
    if count > limit:
        raise HTTPException(429, "Rate limit exceeded")
```

## Logging and Auditing

### Application Logs

**What to log:**
```python
# Successful authentication
logger.info(f"User authenticated: {user_email}")

# Conversation start
logger.info(f"New conversation: user={user_email}, range={range_id}")

# Tool execution
logger.info(f"Tool call: user={user_email}, tool={tool_name}, args={sanitized_args}")

# Tool results (summary only)
logger.info(f"Tool result: user={user_email}, tool={tool_name}, success={success}")

# Errors
logger.error(f"Agent error: user={user_email}, error={error}", exc_info=True)
```

**What NOT to log:**
- JWT tokens (except last 4 chars for debugging)
- Database passwords
- SSH private keys
- Full command outputs (may contain sensitive data)
- User message content (PII)

### Security Events

**Alert on:**
- Failed JWT validation attempts (>3 per user per hour)
- Unauthorized range access attempts
- Excessive tool call rate (>50 per minute)
- MCP connection failures (possible SSH key issue)

**CloudWatch Metric Filters:**
```hcl
resource "aws_cloudwatch_log_metric_filter" "auth_failures" {
  name           = "faceplate-auth-failures"
  log_group_name = aws_cloudwatch_log_group.faceplate.name
  pattern        = "[time, request_id, level=ERROR, msg=\"*Invalid token*\"]"
  
  metric_transformation {
    name      = "AuthFailures"
    namespace = "Faceplate/Security"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "auth_failure_spike" {
  alarm_name          = "faceplate-auth-failure-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "AuthFailures"
  namespace           = "Faceplate/Security"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_actions       = [var.sns_topic_arn]
}
```

### Audit Trail

**Conversation history:**
- All messages persisted (user, assistant, tool)
- Timestamps for every message
- Range ID and user email for every conversation
- Immutable (no updates, only inserts and deletes)

**Tool execution:**
```python
# Log every tool call with full context
audit_log = {
    "timestamp": datetime.utcnow().isoformat(),
    "user_email": user_email,
    "range_id": range_id,
    "tool_name": tool_name,
    "tool_args": tool_args,
    "tool_result_summary": result[:200],  # First 200 chars
    "success": success,
    "error": error if not success else None
}

logger.info(f"AUDIT: {json.dumps(audit_log)}")
```

## Incident Response

### Security Incident Playbook

**1. Unauthorized Access Detected:**
```bash
# Revoke user's JWT (force re-auth)
aws cognito-idp admin-user-global-sign-out \
  --user-pool-id $COGNITO_POOL_ID \
  --username $USER_EMAIL

# Terminate user's active ranges
./scripts/destroy-user-ranges.sh $USER_EMAIL

# Review audit logs
aws logs tail /faceplate/prod --follow --filter-pattern "$USER_EMAIL"
```

**2. SSH Key Compromise:**
```bash
# Rotate compromised key
aws secretsmanager update-secret \
  --secret-id faceplate/ssh-keys/$RANGE_ID \
  --secret-string "$(cat new_key.pem)"

# Restart affected range instances (pick up new key)
./scripts/restart-range.sh $RANGE_ID
```

**3. Data Breach:**
```bash
# Snapshot database for forensics
aws rds create-db-snapshot \
  --db-instance-identifier shifter-prod-rds \
  --db-snapshot-identifier incident-$(date +%Y%m%d-%H%M%S)

# Enable RDS audit logging (if not already)
aws rds modify-db-instance \
  --db-instance-identifier shifter-prod-rds \
  --enable-cloudwatch-logs-exports '["postgresql"]'

# Review affected conversations
psql $DATABASE_URL -c "
  SELECT id, user_email, range_id, created_at
  FROM conversations
  WHERE updated_at > '2025-01-01 00:00:00'
  ORDER BY updated_at DESC;
"
```

## Compliance Considerations

### Data Retention

**Current Policy:**
- Conversations: Retained indefinitely (user can delete)
- Logs: 30 days (CloudWatch)
- Database backups: 7 days (RDS automated)

**GDPR Considerations (if applicable):**
- User can delete their conversations via Portal
- Export conversation history via API (future)
- Right to be forgotten: Delete user + cascade to conversations

### PII Handling

**What is PII:**
- User email (stored, used for auth)
- Conversation content (stored, may contain PII)

**Protections:**
- Encrypted at rest (RDS encryption)
- Encrypted in transit (TLS)
- Access control (JWT validation)
- Not logged (scrubbed from application logs)

## Security Testing

### Automated Scanning

**Dependency scanning:**
```bash
# Python dependencies
uv run pip-audit

# Node dependencies
npm audit

# Container scanning (on ECR push)
# Automatically enabled via Terraform
```

**SAST (Static Analysis):**
```bash
# Python security linting (Ruff includes bandit rules)
uv run ruff check . --select S

# TypeScript security linting
npm run lint
```

**IaC Scanning:**
```bash
# Checkov (already in CI/CD)
checkov -d terraform/ --framework terraform
```

### Manual Testing

**Penetration testing checklist:**
- [ ] JWT validation bypass attempts
- [ ] SQL injection in conversation queries
- [ ] Cross-user conversation access
- [ ] MCP command injection
- [ ] WebSocket hijacking
- [ ] Rate limit bypass
- [ ] SSRF via Bedrock endpoint manipulation

### Bug Bounty Scope (Future)

**In scope:**
- Faceplate backend and frontend
- Authentication bypass
- Authorization bypass
- Data exposure

**Out of scope:**
- DDoS attacks
- Social engineering
- Physical attacks
- Third-party services (Cognito, Bedrock)

## Security Checklist

**Before production deployment:**
- [ ] JWT validation enabled and tested
- [ ] RDS encryption enabled
- [ ] Secrets Manager for all credentials
- [ ] Security groups restrict inbound to ALB only
- [ ] IMDSv2 enforced on EC2
- [ ] TLS 1.3 on ALB
- [ ] CloudWatch alarms configured
- [ ] Audit logging enabled
- [ ] Rate limiting implemented
- [ ] Dependency scanning in CI/CD
- [ ] Penetration testing completed
- [ ] Incident response playbook documented

