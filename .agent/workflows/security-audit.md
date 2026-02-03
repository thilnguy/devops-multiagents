---
description: Perform security audit on infrastructure and deployments
---

# Security Audit Workflow

This workflow guides comprehensive security review across all components.

## Personas Involved
- **Master Architect**: Orchestrator
- **Kube Master**: K8s security review
- **Infra Bot**: Infrastructure security

## MCP Tools Used
- `mcp_kubernetes_resources_list`
- `mcp_github_search_code`

## Steps

### Phase 1: Kubernetes Security Audit (Kube Master)
*Skill Used: `security-audit`*

> @Kube-Master: Ensure cluster security posture by auditing privileges, RBAC, and network policies.

#### 1.1 Check Pod Security

// turbo
```bash
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'
```

Look for pods running as root:
// turbo
```bash
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].securityContext.runAsUser}{"\n"}{end}'
```

#### 1.2 Check RBAC Configuration

List cluster roles:
// turbo
```bash
kubectl get clusterroles | grep -v system
```

Check role bindings:
// turbo
```bash
kubectl get rolebindings -A
```

#### 1.3 Check Secrets

List secrets (don't expose content):
// turbo
```bash
kubectl get secrets -A --no-headers | wc -l
```

Check for default service account tokens:
// turbo
```bash
kubectl get serviceaccounts -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.automountServiceAccountToken}{"\n"}{end}'
```

#### 1.4 Network Policies

// turbo
```bash
kubectl get networkpolicies -A
```

### Phase 2: Terraform Security Review (Infra Bot)
*Skill Used: `security-audit`*

> @Infra-Bot: Ensure infrastructure code is free of secrets and misconfigurations.

#### 2.1 Check for Hardcoded Secrets

// turbo
```bash
grep -r "password\|secret\|key\|token" infra/terraform/ --include="*.tf" | grep -v "variable\|#"
```

#### 2.2 Check S3 Bucket Security

Review for public access:
// turbo
```bash
grep -r "acl\|public" infra/terraform/ --include="*.tf"
```

#### 2.3 Security Groups Audit

Check for open ingress:
// turbo
```bash
grep -A 10 "ingress" infra/terraform/ --include="*.tf" | grep "0.0.0.0/0"
```

### Phase 3: GitHub Repository Security
*Skill Used: `security-audit`*

> @Master-Architect: Ensure repository history contains no credential leaks.

#### 3.1 Check for Exposed Secrets

Using MCP:
```
mcp_github_search_code with q="password repo:owner/devops_multiagents"
```

#### 3.2 Review Branch Protection

Check if main branch is protected via GitHub UI or API.

### Phase 4: Container Image Security

#### 4.1 Dockerfile Best Practices

// turbo
```bash
grep -r "USER\|HEALTHCHECK" services/ --include="Dockerfile"
```

Check for latest tag usage:
// turbo
```bash
grep -r "FROM.*:latest" services/ --include="Dockerfile"
```

### Phase 5: Generate Security Report

Create a report with findings:

```markdown
# Security Audit Report - [DATE]

## Summary
- Critical Issues: X
- High Issues: X
- Medium Issues: X
- Low Issues: X

## Findings

### Critical
- [Finding description]
  - Location: [File/Resource]
  - Remediation: [Steps to fix]

### High
...

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
```

## Security Checklist

- [ ] No hardcoded secrets in code
- [ ] Pods running as non-root
- [ ] Network policies defined
- [ ] RBAC properly configured
- [ ] Secrets encrypted at rest
- [ ] Branch protection enabled
- [ ] Container images scanned
- [ ] TLS enabled for all services

## Escalation

Critical findings should be:
1. Documented immediately
2. Reported to Master Architect
3. Tracked as high-priority issues
