---
name: K8s Troubleshoot
description: Diagnose and resolve Kubernetes cluster issues
---

# Skill: K8s Troubleshoot

**Context:** Use this when @Kube-Master needs to diagnose pod failures, cluster events, or resource issues.

## Required MCP Server
- `kubernetes` (provides `pods_list`, `pods_log`, `events_list`, `resources_get`)

## Workflow

### 1. Identify the Problem
- Use `mcp_kubernetes_pods_list` to see all pods and their statuses.
- Filter by `status.phase` if looking for specific states (Running, Pending, Failed).

### 2. Check Events
- Use `mcp_kubernetes_events_list` to find recent cluster events.
- Look for warnings related to scheduling, resource limits, or image pulls.

### 3. Inspect Logs
- Use `mcp_kubernetes_pods_log` to retrieve container logs.
- Check for application errors or crash stack traces.

### 4. Analyze Resources
- Use `mcp_kubernetes_resources_get` for detailed spec/status of Deployments, Services, etc.
- Verify replicas, selectors, and resource requests/limits.

### 5. Report
- Summarize findings and propose remediation steps to @Master-Architect.
