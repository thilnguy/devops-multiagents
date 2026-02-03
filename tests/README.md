# 🧪 DevOps Validation & Testing Suite

## Overview
This project employs a tiered validation strategy to ensure system stability, security, and persona integrity. We utilize a hybrid execution model capable of running CLI-based tests on the user's terminal and MCP-based tests via agent cognition.

## Validation Tiers

### 1. 🚀 Quick Validation (Smoke Test)
*   **Purpose:** Fast verification of core infrastructure and syntax.
*   **Scope:** 10 Critical Test Cases (CLI only).
*   **Execution Time:** ~30 seconds.
*   **Workflow:** `/agent-validation-quick`
*   **Coverage:**
    *   Terraform Syntax/Validation
    *   Standard Drift Detection
    *   Kubernetes Manifest Linting
    *   Basic Watchdog Logic

### 2. 🛡️ Standard Validation (Daily)
*   **Purpose:** Routine daily checks including external tool connectivity.
*   **Scope:** 17 Test Cases (CLI + MCP).
*   **Execution Time:** ~3 minutes.
*   **Workflow:** `/agent-validation-standard`
*   **Coverage:**
    *   **All Quick Tests**
    *   Kubernetes Pod Status (MCP)
    *   Jenkins Server Health
    *   GitHub Repository Access
    *   Node Capacity Checks

### 3. 🧠 Deep Validation (Release Candidate)
*   **Purpose:** Full system audit before major releases.
*   **Scope:** 25 Comprehensive Test Cases.
*   **Execution Time:** ~10 minutes.
*   **Workflow:** `/agent-validation-deep`
*   **Coverage:**
    *   **All Standard Tests**
    *   Multi-Agent Coordination (Context Handoff)
    *   Security Boundaries (Persona Permissions)
    *   Incident Response Simulation
    *   Approval Gate Enforcement
    *   Race Condition Detection

## Execution Instructions

The Agent manages execution via defined workflows. To trigger a validation run, use the corresponding slash command in the chat interface:

```text
@[/agent-validation-quick]
```

### Report Output
Reports are automatically generated in `tests/results/reports/` with timestamped filenames:
*   `quick-validation-YYYY-MM-DD-HHMM.md`
*   `standard-validation-YYYY-MM-DD-HHMM.md`
*   `deep-validation-YYYY-MM-DD-HHMM.md`

## Test Plans
For detailed definitions of each test case, refer to the [Validation Test Plans](docs/k8s-validation.md).
