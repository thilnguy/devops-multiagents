---
description: Troubleshoot and diagnose Kubernetes pod issues
---

# Kubernetes Troubleshooting Workflow

This workflow guides the Kube Master persona through systematic K8s diagnostics.

## Persona
- **Kube Master**: Primary executor
- **Master Architect**: Escalation point

## MCP Tools Used
- `mcp_kubernetes_pods_list`
- `mcp_kubernetes_pods_log`
- `mcp_kubernetes_events_list`
- `mcp_kubernetes_pods_get`

## Steps

### Step 1: Identify Problem Pods

// turbo
```bash
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
```

Or use MCP:
```
mcp_kubernetes_pods_list with fieldSelector="status.phase=Pending"
```

### Step 2: Check Pod Status Details

For each problematic pod:
// turbo
```bash
kubectl describe pod <POD_NAME> -n <NAMESPACE>
```

Look for:
- **Pending**: Scheduling issues (resources, node selector)
- **CrashLoopBackOff**: Application crash
- **ImagePullBackOff**: Image not found or auth issues

### Step 3: Review Events

// turbo
```bash
kubectl get events -n <NAMESPACE> --sort-by='.lastTimestamp' | tail -20
```

Or use MCP:
```
mcp_kubernetes_events_list with namespace="<NAMESPACE>"
```

### Step 4: Check Container Logs

// turbo
```bash
kubectl logs <POD_NAME> -n <NAMESPACE> --tail=100
```

For crashed containers:
// turbo
```bash
kubectl logs <POD_NAME> -n <NAMESPACE> --previous
```

### Step 5: Resource Analysis

Check node resources:
// turbo
```bash
kubectl top nodes
```

Check pod resources:
// turbo
```bash
kubectl top pods -n <NAMESPACE>
```

### Step 6: Common Fixes

**For OOMKilled:**
```bash
kubectl patch deployment <DEPLOY> -n <NAMESPACE> -p '{"spec":{"template":{"spec":{"containers":[{"name":"<CONTAINER>","resources":{"limits":{"memory":"512Mi"}}}]}}}}'
```

**For ImagePullBackOff:**
```bash
kubectl create secret docker-registry regcred --docker-server=<REGISTRY> --docker-username=<USER> --docker-password=<TOKEN> -n <NAMESPACE>
```

**For CrashLoopBackOff:**
- Check logs for application errors
- Verify environment variables
- Check ConfigMaps and Secrets

### Step 7: Restart Pod (if needed)

```bash
kubectl delete pod <POD_NAME> -n <NAMESPACE>
```

Or restart entire deployment:
```bash
kubectl rollout restart deployment/<DEPLOY> -n <NAMESPACE>
```

## Escalation
If issue persists after 3 diagnosis cycles, escalate to Master Architect with:
- Pod describe output
- Last 100 log lines
- Event timeline
