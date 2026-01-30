---
name: Security Audit
description: Perform security checks on infrastructure and configurations
---

# Skill: Security Audit

**Context:** Use this for periodic security reviews or when investigating potential vulnerabilities.

## Scope
1. **Secret Scanning:** Check for exposed secrets in code or configs.
2. **RBAC Review:** Audit Kubernetes roles and bindings.
3. **Network Policies:** Verify ingress/egress rules.

## Workflow

### 1. Code Secret Scan
- Use `mcp_github_search_code` to find potential secrets in repositories.
- Search patterns: `password=`, `api_key=`, `secret=`.

### 2. K8s RBAC Audit
- Use `mcp_kubernetes_resources_list` with `apiVersion: rbac.authorization.k8s.io/v1` and `kind: ClusterRoleBinding`.
- Check for overly permissive bindings (e.g., `cluster-admin` granted broadly).

### 3. Terraform State Review
- Use `terraform-registry` MCP to review resource configurations.
- Check for publicly exposed resources (S3 buckets, security groups).

### 4. Report
- Document findings with severity levels (Critical, High, Medium, Low).
- Propose remediation steps.
