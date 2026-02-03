# Memory Protocol: Agent Shared State

**Version:** 1.0
**Status:** Active

---

## 🎯 Purpose

This protocol defines how agents share context, learnings, and operational state. The goal is to enable **long-term memory** and **cross-session learning** without requiring a dedicated database infrastructure.

---

## 📦 Storage Location

All shared memory is stored in:
```
.antigravity/state/memory.json
```

---

## 📊 Schema Definition

```json
{
  "version": "1.0",
  "last_updated": "ISO 8601 Timestamp",
  "updated_by": "@PersonaName",

  "health_status": {
    "overall": "HEALTHY | DEGRADED | CRITICAL",
    "last_check": "ISO 8601 Timestamp",
    "details": {
      "kubernetes": "OK | WARNING | ERROR",
      "jenkins": "OK | WARNING | ERROR",
      "infrastructure": "OK | WARNING | ERROR"
    }
  },

  "context_handoff": {
    "vpc_id": "string | null",
    "active_namespace": "string | null",
    "pending_deployments": ["string"],
    "infra_lock": {
      "locked": false,
      "locked_by": "@PersonaName | null",
      "reason": "string | null"
    }
  },

  "learnings": [
    {
      "id": "LRN-001",
      "discovered_by": "@PersonaName",
      "timestamp": "ISO 8601 Timestamp",
      "category": "K8s | Terraform | CI/CD | Security",
      "pattern": "Short description of the learning",
      "resolution": "How it was resolved"
    }
  ],

  "watchdog_exclusions": {
    "description": "Resources that @Watchdog should ignore during health checks",
    "namespaces": ["string - namespace names to skip entirely"],
    "pods": ["string - pod name patterns to skip (supports glob *)"]
  }
}
```

---

## 📝 Access Rules

| Persona | Read | Write (health_status) | Write (context_handoff) | Write (learnings) |
|:---|:---:|:---:|:---:|:---:|
| @Watchdog | ✅ | ✅ | ❌ | ❌ |
| @Infra-Bot | ✅ | ❌ | ✅ | ✅ |
| @Kube-Master | ✅ | ❌ | ✅ | ✅ |
| @Pipe-Liner | ✅ | ❌ | ❌ | ✅ |
| @Master-Architect | ✅ | ✅ | ✅ | ✅ |

---

## 🔄 Update Protocol

1. **Read Before Write:** Always read the current state before updating.
2. **Atomic Updates:** Update one section at a time to avoid conflicts.
3. **Timestamp:** Always update `last_updated` and `updated_by`.
4. **Append-Only Learnings:** Never delete from the `learnings` array.

---
*Maintained by @Master-Architect*
