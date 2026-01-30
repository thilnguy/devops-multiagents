---
description: Daily system health check and monitoring
---

# Daily Health Check Workflow

// turbo-all

This automated workflow performs comprehensive health checks across all systems.

## Personas Involved
- **Master Architect**: Orchestrates checks
- **All Agents**: Execute domain-specific checks

## Schedule
- Run daily at 09:00 AM
- Run on-demand before deployments

## Steps

### Step 1: Kubernetes Health (Kube Master)

Check cluster status:
```bash
kubectl cluster-info
```

Check node health:
```bash
kubectl get nodes
```

Check resource usage:
```bash
kubectl top nodes 2>/dev/null || echo "Metrics server not available"
```

List unhealthy pods:
```bash
kubectl get pods -A | grep -v "Running\|Completed"
```

### Step 2: Application Health

Check deployments:
```bash
kubectl get deployments -n devops-multiagents
```

Check pod readiness:
```bash
kubectl get pods -n devops-multiagents -o wide
```

Check services:
```bash
kubectl get svc -n devops-multiagents
```

### Step 3: Infrastructure State (Infra Bot)

Navigate and check Terraform:
```bash
cd infra/terraform && terraform state list 2>/dev/null | wc -l || echo "No state file"
```

Check for state drift:
```bash
terraform plan -detailed-exitcode 2>/dev/null; echo "Exit code: $?"
```

### Step 4: CI/CD Health (Pipe Liner)

Using MCP to check Jenkins:
```
mcp_jenkins_getStatus
```

Check recent builds:
```
mcp_jenkins_getJobs with limit=5
```

### Step 5: MCP Server Connectivity

Run health check script:
```bash
python3 .antigravity/scripts/mcp-health-check.py
```

### Step 6: Generate Health Report

```markdown
# Daily Health Report - [DATE]

## Overall Status: 🟢 Healthy / 🟡 Degraded / 🔴 Critical

### Kubernetes
- Cluster: [Status]
- Nodes: X/Y Ready
- Pods: X Running, Y Pending, Z Failed

### Applications
- devops-multiagents: [Status]
- Replicas: X/Y Ready

### Infrastructure
- Terraform resources: X managed
- Drift detected: Yes/No

### CI/CD
- Jenkins: [Status]
- Last build: #X - [Status]

### Actions Needed
- [ ] [Action 1]
- [ ] [Action 2]
```

## Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Node CPU | > 70% | > 90% |
| Node Memory | > 75% | > 90% |
| Pod Restarts | > 3/hour | > 10/hour |
| Failed Pods | > 0 | > 3 |

## Auto-Remediation

If issues detected:
1. **Pod CrashLoop**: Restart deployment
2. **High Resource**: Scale horizontally
3. **Drift Detected**: Alert Master Architect

## Notification

After completion, report should be:
- Logged to artifacts/health-reports/
- Sent to Master Architect
- Create issue if Critical status
