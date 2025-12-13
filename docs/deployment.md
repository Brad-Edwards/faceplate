# Deployment

Docker-based deployment on EC2 in Portal VPC.

## Infrastructure Overview

Faceplate deploys alongside Shifter Portal, sharing:
- VPC and subnets
- ALB (path-based routing)
- PostgreSQL RDS
- Cognito User Pool
- Security groups

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.12-slim AS backend-builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy backend dependencies
COPY backend/requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Copy frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

# Copy backend from builder
COPY --from=backend-builder /usr/local /usr/local
COPY backend/app ./app

# Copy frontend build
COPY --from=frontend-builder /app/dist ./frontend/dist

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Multi-stage Benefits:**
- Smaller final image (~200MB vs ~1GB)
- No dev dependencies in production
- Frontend built during image build

### docker-compose.yml (Local Development)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: faceplate_dev
      POSTGRES_USER: faceplate
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  faceplate:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://faceplate:devpassword@postgres:5432/faceplate_dev
      COGNITO_REGION: us-east-1
      COGNITO_USER_POOL_ID: ${COGNITO_USER_POOL_ID}
      COGNITO_CLIENT_ID: ${COGNITO_CLIENT_ID}
      BEDROCK_ENDPOINT: http://localhost:8080
      BEDROCK_MODEL: anthropic.claude-3-5-sonnet-20241022-v2:0
      MCP_KEY_BUCKET: shifter-dev-keys
    depends_on:
      - postgres
    volumes:
      - ./backend/app:/app/app  # Hot reload for dev

volumes:
  postgres_data:
```

**Usage:**
```bash
# Start all services
docker-compose up

# Rebuild after code changes
docker-compose up --build

# Stop and remove
docker-compose down
```

## Terraform Configuration

### EC2 Module

```hcl
# terraform/modules/faceplate/ec2/main.tf

resource "aws_instance" "faceplate" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type
  subnet_id     = var.private_subnet_id
  
  vpc_security_group_ids = [aws_security_group.faceplate.id]
  iam_instance_profile   = aws_iam_instance_profile.faceplate.name
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    ecr_repository = var.ecr_repository_url
    aws_region     = var.aws_region
    environment    = var.environment
  }))
  
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # IMDSv2
    http_put_response_hop_limit = 2
  }
  
  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }
  
  tags = {
    Name        = "shifter-${var.environment}-faceplate"
    Environment = var.environment
    Component   = "faceplate"
  }
}

resource "aws_security_group" "faceplate" {
  name_prefix = "shifter-${var.environment}-faceplate-"
  vpc_id      = var.vpc_id
  
  # Inbound from ALB only
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }
  
  # Outbound to RDS
  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.rds_security_group_id]
  }
  
  # Outbound to NAT (for Cognito, Bedrock, MCP)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "shifter-${var.environment}-faceplate-sg"
  }
}

resource "aws_iam_role" "faceplate" {
  name = "shifter-${var.environment}-faceplate-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.faceplate.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "faceplate" {
  name = "shifter-${var.environment}-faceplate-policy"
  role = aws_iam_role.faceplate.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:*:secret:faceplate/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.ssh_key_bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "faceplate" {
  name = "shifter-${var.environment}-faceplate-profile"
  role = aws_iam_role.faceplate.name
}
```

### ALB Target Group

```hcl
# terraform/modules/faceplate/alb/main.tf

resource "aws_lb_target_group" "faceplate" {
  name     = "shifter-${var.environment}-faceplate"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
  
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 3600
    enabled         = true
  }
  
  tags = {
    Name = "shifter-${var.environment}-faceplate-tg"
  }
}

resource "aws_lb_target_group_attachment" "faceplate" {
  target_group_arn = aws_lb_target_group.faceplate.arn
  target_id        = var.faceplate_instance_id
  port             = 8000
}

resource "aws_lb_listener_rule" "faceplate" {
  listener_arn = var.alb_listener_arn
  priority     = 100
  
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.faceplate.arn
  }
  
  condition {
    path_pattern {
      values = ["/chat*", "/ws*", "/static*"]
    }
  }
}
```

### Secrets Manager

```hcl
# terraform/modules/faceplate/secrets/main.tf

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "faceplate/${var.environment}/db-credentials"
  recovery_window_in_days = 0  # Allow immediate deletion for dev
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  
  secret_string = jsonencode({
    username = "faceplate_${var.environment}"
    password = random_password.db_password.result
    host     = var.rds_endpoint
    port     = 5432
    database = "faceplate_${var.environment}"
    url      = "postgresql://faceplate_${var.environment}:${random_password.db_password.result}@${var.rds_endpoint}:5432/faceplate_${var.environment}"
  })
}
```

### Environment Configuration

```hcl
# terraform/environments/dev/faceplate/main.tf

module "faceplate_ec2" {
  source = "../../../modules/faceplate/ec2"
  
  environment           = "dev"
  instance_type         = "t3.medium"
  vpc_id                = data.terraform_remote_state.portal.outputs.vpc_id
  private_subnet_id     = data.terraform_remote_state.portal.outputs.private_subnet_ids[0]
  alb_security_group_id = data.terraform_remote_state.portal.outputs.alb_security_group_id
  rds_security_group_id = data.terraform_remote_state.portal.outputs.rds_security_group_id
  ecr_repository_url    = aws_ecr_repository.faceplate.repository_url
  aws_region            = "us-east-1"
  ssh_key_bucket        = "shifter-dev-keys"
}

module "faceplate_alb" {
  source = "../../../modules/faceplate/alb"
  
  environment          = "dev"
  vpc_id               = data.terraform_remote_state.portal.outputs.vpc_id
  alb_listener_arn     = data.terraform_remote_state.portal.outputs.alb_listener_arn
  faceplate_instance_id = module.faceplate_ec2.instance_id
}

resource "aws_ecr_repository" "faceplate" {
  name                 = "shifter/faceplate"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = "AES256"
  }
}
```

## User Data Script

```bash
#!/bin/bash
# user_data.sh

set -e

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Login to ECR
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_repository}

# Pull image
docker pull ${ecr_repository}:latest

# Fetch secrets
DB_SECRET=$(aws secretsmanager get-secret-value --secret-id faceplate/${environment}/db-credentials --query SecretString --output text)
DATABASE_URL=$(echo $DB_SECRET | jq -r .url)

# Run container
docker run -d \
  --name faceplate \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e COGNITO_REGION=${aws_region} \
  -e COGNITO_USER_POOL_ID=${cognito_user_pool_id} \
  -e COGNITO_CLIENT_ID=${cognito_client_id} \
  -e BEDROCK_ENDPOINT=${bedrock_endpoint} \
  -e MCP_KEY_BUCKET=${mcp_key_bucket} \
  ${ecr_repository}:latest

# Configure log rotation
cat > /etc/logrotate.d/docker-faceplate <<EOF
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size 50M
  missingok
  delaycompress
  copytruncate
}
EOF
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/faceplate.yml

name: Faceplate

on:
  push:
    branches: [main, dev]
    paths:
      - 'backend/**'
      - 'frontend/**'
      - 'terraform/modules/faceplate/**'
      - '.github/workflows/faceplate.yml'
  pull_request:
    paths:
      - 'backend/**'
      - 'frontend/**'
      - 'terraform/modules/faceplate/**'

permissions:
  contents: read
  id-token: write

jobs:
  test-backend:
    name: Test Backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: astral-sh/setup-uv@v4
      
      - name: Install dependencies
        working-directory: backend
        run: uv sync --group dev
      
      - name: Lint Python
        working-directory: backend
        run: |
          uv run ruff check .
          uv run ruff format --check .
      
      - name: Run tests
        working-directory: backend
        run: uv run pytest --cov

  test-frontend:
    name: Test Frontend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Lint TypeScript
        working-directory: frontend
        run: npm run lint
      
      - name: Build
        working-directory: frontend
        run: npm run build

  terraform-plan:
    name: Terraform Plan
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      
      - uses: hashicorp/setup-terraform@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Terraform Init
        working-directory: terraform/environments/dev/faceplate
        run: terraform init
      
      - name: Terraform Plan
        working-directory: terraform/environments/dev/faceplate
        run: terraform plan -no-color
        continue-on-error: true

  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/dev'
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Login to ECR
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.ecr-login.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/shifter/faceplate:$IMAGE_TAG .
          docker push $ECR_REGISTRY/shifter/faceplate:$IMAGE_TAG
          docker tag $ECR_REGISTRY/shifter/faceplate:$IMAGE_TAG $ECR_REGISTRY/shifter/faceplate:latest
          docker push $ECR_REGISTRY/shifter/faceplate:latest
      
      - name: Apply Terraform
        working-directory: terraform/environments/${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}/faceplate
        run: |
          terraform init
          terraform apply -auto-approve
      
      - name: Deploy to EC2
        env:
          ENVIRONMENT: ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}
        run: |
          INSTANCE_ID=$(aws ec2 describe-instances \
            --filters "Name=tag:Component,Values=faceplate" "Name=tag:Environment,Values=$ENVIRONMENT" \
            --query 'Reservations[0].Instances[0].InstanceId' \
            --output text)
          
          aws ssm send-command \
            --instance-ids $INSTANCE_ID \
            --document-name "AWS-RunShellScript" \
            --parameters 'commands=[
              "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REGISTRY",
              "docker pull $ECR_REGISTRY/shifter/faceplate:latest",
              "docker stop faceplate || true",
              "docker rm faceplate || true",
              "docker run -d --name faceplate --restart unless-stopped -p 8000:8000 --env-file /etc/faceplate.env $ECR_REGISTRY/shifter/faceplate:latest"
            ]' \
            --output text
      
      - name: Wait for health check
        run: |
          for i in {1..30}; do
            if curl -f https://shifter.example.com/health; then
              echo "Health check passed"
              exit 0
            fi
            echo "Waiting for service to be healthy..."
            sleep 10
          done
          echo "Health check failed"
          exit 1
```

## Database Migrations

### Initial Schema Setup

```sql
-- migrations/001_initial_schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    range_id UUID NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_range ON conversations(user_email, range_id);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_results JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);

CREATE TABLE mcp_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    range_id UUID NOT NULL UNIQUE,
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER mcp_configs_updated_at
    BEFORE UPDATE ON mcp_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### Migration Script

```bash
#!/bin/bash
# scripts/migrate.sh

set -e

echo "Running database migrations..."

# Get database credentials from Secrets Manager
DB_SECRET=$(aws secretsmanager get-secret-value \
  --secret-id faceplate/dev/db-credentials \
  --query SecretString \
  --output text)

DATABASE_URL=$(echo $DB_SECRET | jq -r .url)

# Run migrations
for migration in migrations/*.sql; do
  echo "Applying $migration..."
  psql "$DATABASE_URL" -f "$migration"
done

echo "Migrations complete!"
```

## Monitoring

### CloudWatch Alarms

```hcl
# terraform/modules/faceplate/monitoring/main.tf

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "faceplate-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Faceplate EC2 CPU usage is above 80%"
  alarm_actions       = [var.sns_topic_arn]
  
  dimensions = {
    InstanceId = var.instance_id
  }
}

resource "aws_cloudwatch_metric_alarm" "health_check_failed" {
  alarm_name          = "faceplate-${var.environment}-unhealthy"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Faceplate health check failing"
  alarm_actions       = [var.sns_topic_arn]
  
  dimensions = {
    TargetGroup  = var.target_group_arn_suffix
    LoadBalancer = var.load_balancer_arn_suffix
  }
}
```

### Log Aggregation

```hcl
resource "aws_cloudwatch_log_group" "faceplate" {
  name              = "/faceplate/${var.environment}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_stream" "application" {
  name           = "application"
  log_group_name = aws_cloudwatch_log_group.faceplate.name
}
```

## Rollback Procedure

### Automatic Rollback on Health Check Failure

```bash
#!/bin/bash
# scripts/deploy-with-rollback.sh

set -e

ECR_REGISTRY="123456789.dkr.ecr.us-east-1.amazonaws.com"
IMAGE_TAG="$1"

# Deploy new version
docker pull $ECR_REGISTRY/shifter/faceplate:$IMAGE_TAG
docker tag $ECR_REGISTRY/shifter/faceplate:$IMAGE_TAG $ECR_REGISTRY/shifter/faceplate:rollback
docker stop faceplate
docker rm faceplate
docker run -d --name faceplate -p 8000:8000 --env-file /etc/faceplate.env $ECR_REGISTRY/shifter/faceplate:$IMAGE_TAG

# Wait for health check
for i in {1..30}; do
  if curl -f http://localhost:8000/health; then
    echo "Deployment successful!"
    exit 0
  fi
  sleep 5
done

# Rollback
echo "Health check failed, rolling back..."
docker stop faceplate
docker rm faceplate
docker run -d --name faceplate -p 8000:8000 --env-file /etc/faceplate.env $ECR_REGISTRY/shifter/faceplate:rollback

echo "Rolled back to previous version"
exit 1
```

## Backup and Recovery

### Database Backups

RDS automated backups handle this (configured in Portal infrastructure).

### Application State

No persistent application state outside database - stateless design.

## Scaling Strategy

### Current (MVP)

- Single EC2 instance
- Handles ~50 concurrent users
- Vertical scaling: Upgrade to t3.large if needed

### Future Growth

**Horizontal Scaling:**
1. Add second EC2 instance
2. ALB distributes traffic
3. Sticky sessions for WebSocket continuity
4. PostgreSQL connection pooling prevents DB bottleneck

**When to scale:**
- CPU >80% sustained
- Memory >70% sustained
- WebSocket connections >40

