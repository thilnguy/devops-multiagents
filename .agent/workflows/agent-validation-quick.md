---
description: Quick smoke test - CLI only (8 TCs, ~30 sec)
---

# Agent Validation - Quick

Fast CLI-based smoke test for minor code changes.

## Coverage
TC-001, TC-002, TC-003, TC-004, TC-007, TC-NEW-001, TC-NEW-002, TC-NEW-003, TC-NEW-008, TC-NEW-011

## Verification ID Pattern (TC-NEW-001)

> [!IMPORTANT]
> Agent generates unique Execution ID. User must include it in command output to prove actual execution.

**How it works:**
1. Agent generates: `VERIFY:exec-XXXX` (random 4 digits)
2. User runs command with `&& echo "VERIFY:exec-XXXX"`
3. Agent validates ID in output before accepting results

## Execution

1. Agent generates a unique verification ID (replace `XXXX` with random 4 digits) and provides this command to the user.
   > **⚠️ PROMPT TO USER:** "Please run this command in your terminal and paste the result here:"
   
   ```text
   sh tests/scripts/run_hybrid_suite.sh --verify=exec-XXXX
   ```

2. User runs in terminal and pastes output

3. Agent checks for specific pass confirmations in the output:
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

4. Agent validates results:
   - ✅ All 9 Pass Messages Found + ID Verified → Accept results
   - ❌ Any Missing → Reject, report missing TCs

## Reporting

5. If validation passes, Agent creates a report file at `tests/results/reports/quick-validation-$(date +%Y-%m-%d-%H%M).md` with the following content (replace variables dynamically):

   ```markdown
   # 🧪 DevOps Multi-Agent Ecosystem: Quick Validation Report
   - **Version:** v2.1-Quick
   - **Date:** $(date +%Y-%m-%d\ %H:%M)
   - **Run ID:** exec-XXXX
   - **Status:** [INSERT STATUS]
   
   ## 📊 Executive Summary
   Quick smoke test execution of 10 critical test cases.
   
   | Category | Total | PASS | FAIL | Result |
   |---|---|---|---|---|
   | Infrastructure & Core | 10 | [INSERT PASS COUNT] | [INSERT FAIL COUNT] | [INSERT PERCENTAGE] |

   ## 🔍 Detailed Breakdown
   *Verified via User Terminal*
   
   - **TC-001 (Terraform):** [INSERT RESULT]
   - **TC-007 (TF Error Detect):** [INSERT RESULT]
   - **TC-NEW-002 (TF Drift):** [INSERT RESULT]
   - **TC-002 (K8s Manifests):** [INSERT RESULT]
   - **TC-003/004 (Sandbox):** [INSERT RESULT]
   - **TC-NEW-008 (Update):** [INSERT RESULT]
   - **TC-NEW-001 (Verification):** [INSERT RESULT]
   - **TC-NEW-003 (Context):** [INSERT RESULT]
   - **TC-NEW-011 (Watchdog):** [INSERT RESULT]

   **Verdict:** [INSERT VERDICT]
   ```

## Expected
- 10/10 PASS (Covering 10 TCs in 9 check steps)
- Report generated in `tests/results/reports/`
- Duration: ~30 seconds
