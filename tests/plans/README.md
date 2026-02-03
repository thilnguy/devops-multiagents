# 🧪 Agent Validation Suite

This directory contains the comprehensive testing framework for the **DevOps Multi-Agent Ecosystem**. It validates agent personas, multi-agent coordination, security guardrails, and autonomous decision-making.

## 📂 Directory Structure

```text
tests/agent-validation/
├── README.md                    # This file (Suite Overview)
├── test-plan-v1.1.md            # Foundational validation (Phase 1-6)
├── test-plan-v2.1.md            # Advanced security & resilience (Phase 7-10)
├── executive_summary_v1.1.md    # Analysis of Phase 1-6 results
├── executive_summary_v2.1.md    # Deep dive analysis of Phase 7-10 results
├── suite_review.md              # Health check and architecture review of the test suite
├── fixtures/                    # Test data and intentionally buggy assets
│   ├── sandbox-namespace.yaml   # K8s isolation environment
│   ├── buggy-deployment.yaml    # ImagePullBackOff scenario
│   ├── crash-loop-app.yaml      # CrashLoopBackOff scenario
│   └── invalid-terraform.tf     # Terraform syntax error scenario
└── results/                    # [Placeholder] Execution logs and artifacts
```

## ⚙️ Execution Model (Hybrid)

Due to sandbox network restrictions, we use a **Shared Responsibility Model**:
- 👤 **USER:** Executes Infrastructure CLI commands (`terraform`, `kubectl`) in the local terminal to bridge network gaps.
- 🤖 **AGENT:** Operates as the **Architect & Validator**. Agents use MCP tools (GitHub, Jenkins, Kubernetes) to inspect state, diagnose errors, and verify user actions.

## 📋 Validation Phases

### Phase 1-6: Foundational Integrity
Detailed in `test-plan-v1.1.md`. Focuses on individual persona competence (Infra-Bot, Kube-Master, Pipe-Liner) and basic orchestration.

### Phase 7-10: Advanced Resilience & Security
Detailed in `test-plan-v2.1.md`. Covers:
- **Zero-Trust Verification:** Nonce-based command confirmation.
- **Security Guardrails:** Anti-prompt injection and persona boundaries.
- **Day-2 Operations:** Drift detection and zero-downtime updates.
- **Autonomous Safety:** Hallucination checks and idempotency.

## 📊 Quick Start

To review the latest validation results and architectural assessment, refer to:
- [Executive Summary v1.1](./executive_summary_v1.1.md)
- [Executive Summary v2.1](./executive_summary_v2.1.md)

---
*Maintained by @Master-Architect*
