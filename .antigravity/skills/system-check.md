---
name: System Check
description: Verify MCP connections and project structure
---

# Skill: System Health Check

**Context:** Use this to verify all MCP servers and project structures are correctly configured before starting work.

## Required Script
- `.antigravity/scripts/mcp-health-check.py`

## Workflow

### 1. Execute Health Check
```bash
python3 .antigravity/scripts/mcp-health-check.py
```

### 2. Interpret Results
- ✅ = Ready to use.
- ⚠️ = Warning, may need attention.
- ❌ = Error, must fix before proceeding.

### 3. On Failure
If any check fails, @Master-Architect should:
1. Identify the failing component (MCP server, CLI tool, config file).
2. Request user to fix credentials or install missing tools.
3. Re-run the health check until all green.

### 4. On Success
List available MCP tools for each server, e.g.:
- `github`: `create_issue`, `create_pull_request`, `search_code`
- `kubernetes`: `pods_list`, `pods_log`, `events_list`
- `jenkins`: `triggerBuild`, `getBuild`, `getJob`