# Agent Coordination Protocol

**Version:** 1.0  
**Status:** Active  
**Purpose:** Prevent agent conflicts and oscillation loops

---

## 1. Agent Priority Hierarchy

When agents have conflicting decisions, higher priority wins:

| Priority | Agent | Domain | Override Authority |
|:---:|:---|:---|:---|
| 1 | **Master-Architect** | Strategy & Approval | Can override all |
| 2 | **Watchdog** | Health & Stability | Can pause cost actions |
| 3 | **Infra-Bot** | Infrastructure | Follows health directives |
| 4 | **Kube-Master** | Deployments | Follows infra state |
| 5 | **Pipe-Liner** | CI/CD | Lowest priority |

---

## 2. Cooldown Periods

Minimum time between related actions to prevent oscillation:

| Action Type | Cooldown | Rationale |
|:---|:---:|:---|
| Scale Up/Down | 10 min | Allow metrics to stabilize |
| Cost Optimization | 30 min | Prevent thrashing |
| Rollback | 15 min | Let deployment settle |
| Alert Re-escalation | 5 min | Avoid duplicate alerts |

---

## 3. Circuit Breaker Rules

**Trigger:** 3+ conflicting actions within 15 minutes

**Actions:**
1. **PAUSE** all automated remediation
2. **ALERT** Master-Architect immediately
3. **LOG** conflict chain to memory.json
4. **REQUIRE** human approval to resume

```python
# Pseudo-code for circuit breaker
if action_count_in_window(action_type="scale", window=15_min) >= 3:
    trigger_circuit_breaker()
    alert_master_architect("Oscillation detected: scaling loop")
```

---

## 4. Conflict Resolution Matrix

| Scenario | Winner | Action |
|:---|:---|:---|
| Watchdog detects issue + Cost Agent wants shutdown | Watchdog | Delay shutdown until resolved |
| Infra-Bot scaling + Watchdog debugging | Watchdog | Infra-Bot pauses scaling |
| Multiple Terraform applies | First lock holder | Others wait + retry |
| Cost spike + Active incident | Watchdog | Cost action deferred |

---

## 5. Communication Protocol

### Inter-Agent Signals
Agents MUST check memory.json before destructive actions:

```json
{
  "agent_locks": {
    "infra-bot": {
      "action": "terraform_apply",
      "started": "2026-02-04T10:00:00Z",
      "ttl_minutes": 30
    }
  },
  "cooldowns": {
    "scale_down": "2026-02-04T10:30:00Z"
  }
}
```

### Escalation Chain
```
Agent → memory.json check → Conflict? → Master-Architect → Human
```

---

## 6. Implementation Checklist

- [ ] Add cooldown checks to Watchdog before scaling alerts
- [ ] Add lock acquisition to Infra-Bot before terraform apply
- [ ] Add conflict detection to Master-Architect decision tree
- [ ] Create `check_agent_lock()` utility function
- [ ] Log all agent actions to memory.json with timestamps

---

*Maintained by @Master-Architect*
