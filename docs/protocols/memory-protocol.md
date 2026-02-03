# Memory Protocol: Agent Shared State (RAG Architecture)

**Version:** 2.0
**Status:** Active
**Architecture:** Retrieval-Augmented Generation (RAG)

---

## 🎯 Purpose

This protocol defines how agents share context while maintaining **Token Efficiency**. Instead of loading the entire history, Agents use a **Retrieval-First** approach.

---

## 📦 Storage Strategy

| Storage | File | Content | Access Method |
|:---|:---|:---|:---|
| **Active Memory** | `.antigravity/state/memory.json` | Current Health, Lock Status, Last 10 Learnings | Direct Load |
| **Archived Memory** | `.antigravity/state/archived_memory.json` | Historical Learnings, Resolved Patterns | **Tool Retrieval Only** |

---

## 📊 Schema Definition

### Active Memory (`memory.json`)
```json
{
  "version": "2.0",
  "last_updated": "ISO 8601 Timestamp",
  "updated_by": "@PersonaName",

  "health_status": {
    "overall": "HEALTHY | DEGRADED | CRITICAL",
    "details": { ... }
  },

  "context_handoff": {
    "vpc_id": "string",
    "active_namespace": "string",
    "infra_lock": { "locked": false, "reason": null }
  },

  "recent_learnings": [
    { "id": "LRN-100", "pattern": "...", "resolution": "..." }
    // Max 10 items. Older items moved to Archive by scripts/archive_memory.py
  ]
}
```

---

## 🛠️ Tool Usage Guidelines

### 1. Reading Context
- **Do NOT** read `archived_memory.json` directly.
- **ALWAYS** read `memory.json` for current operational state.

### 2. Solving Problems (RAG Workflow)
When encountering an error:
1.  **Check Active Memory:** Is the solution in `recent_learnings`?
2.  **Search Archive:** Use `scripts/search_memory.py "error keywords"`
3.  **Analyze Logs:** Use `scripts/analyze_logs.py log_file` to cluster errors.

### 3. Writing Learnings
- Append new key learnings to `memory.json`.
- The **Archiver Job** (`scripts/archive_memory.py`) will automatically migrate old items to the archive.

---

## 📝 Access Rules

| Persona | Active Memory | Archive Retrieval | Write Learnings |
|:---|:---:|:---:|:---:|
| @Watchdog | Read/Write | ✅ | ✅ |
| @Infra-Bot | Read | ✅ | ✅ |
| @Master-Architect | Read/Write | ✅ | ✅ |

---
*Maintained by @Master-Architect*
