---
name: Approval Gate
description: Approval gate for destructive operations
---

# Skill: Approval Gate

**Context:** Use this when a domain agent (@Infra-Bot, @Kube-Master) needs authorization for destructive operations.

## Scope

Operations requiring approval:
- `terraform apply` (production)
- `terraform destroy`
- `kubectl delete` (pods, deployments, namespaces)
- Database migrations
- Security configuration changes

## Approval Process

### Step 1: Request Submission

Domain agent submits request with:
```markdown
## Approval Request

**Agent:** @Infra-Bot / @Kube-Master
**Operation:** [describe operation]
**Impact:** [what will be affected]
**Reversible:** Yes / No
**Urgency:** Low / Medium / High / Critical

### Planned Commands
```bash
[exact commands to be executed]
``` 
```

### Step 2: Master Architect Review

@Master-Architect evaluates:
- [ ] Is the operation necessary?
- [ ] Are there safer alternatives?
- [ ] Is the blast radius acceptable?
- [ ] Is rollback plan documented?

### Step 3: Decision

**Approved:**
```
✅ APPROVED by @Master-Architect
Proceed with execution.
```

**Rejected:**
```
❌ REJECTED by @Master-Architect
Reason: [explanation]
Alternative: [suggested approach]
```

**Deferred:**
```
⏸️ DEFERRED by @Master-Architect
Requires: [additional information needed]
```

## Auto-Approval Criteria

The following may proceed WITHOUT explicit approval:
- Read-only operations (`terraform plan`, `kubectl get`)
- Non-production environments (dev, staging)
- Rollback to known-good state
- Health checks and diagnostics

## Audit Trail

All approval requests must be logged to: `.antigravity/logs/approval.log`

**Log Format:**
`| YYYY-MM-DD HH:MM | @Agent | Operation | ✅/❌/⏸️ | @Master-Architect | Reason/Notes |`

**Example:**
`| 2026-01-30 14:00 | @Infra-Bot | terraform apply | ✅ Approved | @Master-Architect | Emergency fix |`
