# Production Deployment Guide

This guide covers the steps required to deploy the DevOps Multi-Agent Ecosystem in a production environment.

## Prerequisites

Before deploying to production, ensure you have:

- [ ] AWS Account with appropriate IAM permissions
- [ ] Kubernetes cluster (EKS, GKE, or self-managed)
- [ ] Jenkins instance (or equivalent CI/CD platform)
- [ ] GitHub repository access
- [ ] SSL certificates for HTTPS
- [ ] Agent personas configured (see `docs/personas/`)
- [ ] Shared memory store initialized (`artifacts/agent-memory.json`)

## Pre-Deployment Checklist

### 1. Credentials and Secrets

```bash
# Verify MCP configuration
python3 tests/validate_ecosystem.py

# Check all credentials are set
cat ~/.gemini/antigravity/mcp_config.json | jq '.mcpServers | keys'
```

**Required credentials:**
- [ ] GitHub Personal Access Token (with repo and workflow scopes)
- [ ] Jenkins API Token
- [ ] AWS Access Keys or IAM Role
- [ ] Kubernetes cluster credentials

### 2. Infrastructure Setup

#### Terraform State Backend

Before deploying, set up remote state:

```bash
# Create S3 bucket for state
aws s3 mb s3://devops-multiagents-tfstate --region eu-west-1

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name devops-multiagents-tflock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Uncomment backend configuration in infra/terraform/main.tf
```

#### Terraform Deployment

```bash
cd infra/terraform

# Initialize with backend
terraform init

# Create production tfvars
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with production values

# Plan and review
terraform plan -var-file=terraform.tfvars -out=prod.tfplan

# Apply (after review)
terraform apply prod.tfplan
```

### 3. Kubernetes Deployment

#### Namespace Setup

```bash
cd infra/kubernetes/base

# Create namespace first
kubectl apply -f namespace.yaml

# Verify quota
kubectl describe resourcequota -n devops-multiagents
```

#### Deploy Application

```bash
# Using Kustomize
kubectl apply -k .

# Or individually
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Verify deployment
kubectl get pods -n devops-multiagents
kubectl get svc -n devops-multiagents
```

### 4. CI/CD Pipeline

Configure Jenkins with the following:

1. **Credentials:**
   - GitHub credentials for webhooks
   - AWS credentials for Terraform
   - Kubernetes config for deployments

2. **Pipeline Job:**
   - Point to `pipelines/jenkins/Jenkinsfile`
   - Enable webhook triggers

3. **Environment Variables:**
   ```
   TERRAFORM_DIR=infra/terraform
   K8S_DIR=infra/kubernetes/base
   AWS_REGION=eu-west-1
   ```

## Deployment Stages

### Stage 1: Development

1. Deploy infrastructure with `environment = "dev"`
2. Use single NAT gateway
3. Enable debug logging
4. Run integration tests

### Stage 2: Staging

1. Deploy with `environment = "staging"`
2. Run load tests
3. Verify monitoring and alerting
4. Test rollback procedures

### Stage 3: Production

1. Deploy with `environment = "production"`
2. Enable VPC flow logs
3. Configure multi-AZ NAT gateways
4. Enable all security features

## Monitoring and Observability

### Metrics to Monitor

- Pod resource usage (CPU, memory)
- API response times
- Error rates
- Infrastructure costs

### Alerting Rules

Set up alerts for:
- Pod crashes or restarts
- High CPU/memory usage (>80%)
- Failed deployments
- Security events

## Rollback Procedures

### Kubernetes Rollback

```bash
# View deployment history
kubectl rollout history deployment/sample-api -n devops-multiagents

# Rollback to previous version
kubectl rollout undo deployment/sample-api -n devops-multiagents

# Rollback to specific revision
kubectl rollout undo deployment/sample-api -n devops-multiagents --to-revision=2
```

### Terraform Rollback

```bash
# View state history
terraform state list

# Restore from backup
terraform state pull > backup.tfstate
# ... fix issues ...
terraform state push backup.tfstate
```

## Security Hardening

### Network Security

- [ ] Configure Network Policies
- [ ] Enable VPC flow logs
- [ ] Set up WAF rules
- [ ] Configure security groups

### Application Security

- [ ] Enable Pod Security Policies/Standards
- [ ] Run as non-root user
- [ ] Read-only root filesystem
- [ ] Drop all capabilities

### Secret Management

- [ ] Use AWS Secrets Manager or Vault
- [ ] Rotate credentials regularly
- [ ] Enable audit logging
- [ ] Implement least privilege

## Disaster Recovery

### Backup Strategy

1. **Terraform State:** S3 versioning enabled
2. **Kubernetes:** Velero for cluster backups
3. **Application Data:** Regular database backups

### Recovery Time Objectives

| Component | RTO | RPO |
|-----------|-----|-----|
| Infrastructure | 30 min | 0 |
| Application | 15 min | 0 |
| Data | 1 hour | 15 min |

## Troubleshooting

### Common Issues

1. **Pods not starting:**
   ```bash
   kubectl describe pod <pod-name> -n devops-multiagents
   kubectl logs <pod-name> -n devops-multiagents
   ```

2. **Terraform state lock:**
   ```bash
   terraform force-unlock <lock-id>
   ```

3. **Jenkins build failures:**
   - Check credentials
   - Verify workspace permissions
   - Review build logs

For more troubleshooting, refer to individual component logs (Jenkins, K8s events).
