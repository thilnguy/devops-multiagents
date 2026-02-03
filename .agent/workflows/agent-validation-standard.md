---
description: Standard validation - CLI + MCP (17 TCs, ~3 min)
---

# Agent Validation - Standard

Daily validation including CLI and MCP tool tests.

## Coverage
**Quick tier (8)** + TC-005, TC-006, TC-008, TC-009, TC-010, TC-NEW-002, TC-NEW-004, TC-NEW-010, TC-NEW-011

## Verification ID Pattern

> Agent generates `VERIFY:exec-XXXX`. User must include in output to validate execution.

---

## Phase 1: CLI Tests

1. Agent generates a unique verification ID (replace `XXXX` with random 4 digits) and provides this command to the user.
   > **⚠️ PROMPT TO USER:** "Please run this command in your terminal and paste the result here:"
   
   ```text
   sh tests/scripts/run_hybrid_suite.sh --verify=exec-XXXX
   ```
   
   **Agent checks for specific pass confirmations in Phase 1 output:**
   - `VERIFY:exec-XXXX` (Must match generated ID)
   - `✅ TC-001 PASS`
   - `✅ TC-007 PASS`
   - `✅ TC-NEW-002 PASS`
   - `✅ TC-002 PASS`
   - `✅ TC-003/004 PASS`
   - `✅ TC-NEW-008 PASS`
   - `✅ TC-NEW-001 PASS`
   - `✅ TC-NEW-003 PASS`
   - `✅ TC-NEW-011 PASS`

## Phase 2: MCP Tool Tests

2. @Kube-Master: Check pod status for TC-005/006:
   - Execute `mcp_kubernetes_pods_list_in_namespace` (devops-sandbox)
   - Diagnose any ImagePullBackOff or CrashLoopBackOff

3. @Pipe-Liner: Verify Jenkins (TC-009):
   - Execute `mcp_jenkins_getStatus`

4. @Master-Architect: Verify GitHub (TC-010):
   - Execute `mcp_github_list_commits` (thilnguy/devops-multiagents)

## Phase 3: Agent Logic Tests

5. TC-NEW-002: (Mocked in Phase 1) - Verified via CLI.

6. TC-NEW-004: Check node capacity:
   - Execute `mcp_kubernetes_resources_list` (apiVersion="v1", kind="Node") to get allocatable resources.

7. TC-NEW-010: Check audit log:
   - Verify `artifacts/approval-log.md` exists.
   - If missing, note as "No audit history" (PASS).

8. TC-NEW-011: Verify watchdog memory:
// turbo
```bash
if [ -f .antigravity/state/memory.json ]; then cat .antigravity/state/memory.json | grep -A2 "exclusions" | head -5; else echo "Memory file not found - SKIP"; fi
```

## Reporting

9. Agent creates a report file at `tests/results/reports/standard-validation-$(date +%Y-%m-%d-%H%M).md` with the following content (replace variables dynamically):

   ```markdown
   # 🧪 DevOps Multi-Agent Ecosystem: Standard Validation Report
   - **Version:** v2.1-Standard
   - **Date:** $(date +%Y-%m-%d\ %H:%M)
   - **Run ID:** exec-XXXX
   - **Status:** [INSERT STATUS]

   ## 📊 Executive Summary
   Standard validation including CLI smoke tests and MCP connectivity checks.
   
   | Category | Total | PASS | FAIL/SKIP | Result |
   |---|---|---|---|---|
   | Infrastructure (CLI) | 10 | [INSERT CLI PASS] | [INSERT CLI FAIL] | [INSERT CLI %] |
   | MCP & Agent Logic | 8 | [INSERT MCP PASS] | [INSERT MCP FAIL] | [INSERT MCP %] |

   ## 🔍 Detailed Breakdown
   
   ### 1. CLI Tests (Base)
   - **TC-001 (Terraform):** [INSERT RESULT]
   - **TC-007 (TF Error Detect):** [INSERT RESULT]
   - **TC-NEW-002 (TF Drift):** [INSERT RESULT]
   - **TC-002 (K8s Manifests):** [INSERT RESULT]
   - **TC-003/004 (Sandbox):** [INSERT RESULT]
   - **TC-NEW-008 (Update):** [INSERT RESULT]
   - **TC-NEW-001 (Verification):** [INSERT RESULT]
   - **TC-NEW-003 (Context):** [INSERT RESULT]
   - **TC-NEW-011 (Watchdog CLI):** [INSERT RESULT]

   ### 2. MCP & Agent Logic (Advanced)
   - **TC-005/006 (K8s Pods):** [INSERT RESULT]
   - **TC-009 (Jenkins Status):** [INSERT RESULT]
   - **TC-010 (GitHub Commits):** [INSERT RESULT]
   - **TC-NEW-002 (TF Drift):** [INSERT RESULT] (Verified in CLI)
   - **TC-NEW-004 (Node Cap):** [INSERT RESULT]
   - **TC-NEW-010 (Audit Log):** [INSERT RESULT]
   - **TC-NEW-011 (Watchdog Mem):** [INSERT RESULT]

   **Verdict:** [INSERT VERDICT]
   ```

## Expected
- 18/18 PASS (9 CLI + 9 MCP/Logic)
- Report generated in `tests/results/reports/`
- Duration: ~3 minutes
