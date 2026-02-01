# DevOps Multi-Agent System - Test Plan

**Version:** 1.1 | **Updated:** 2026-02-01

---

## ⚙️ Execution Model

> **Important:** Due to sandbox network restrictions, this test plan uses a **hybrid execution model:**

| Task Type | Executor | Validator |
|-----------|:--------:|:---------:|
| **Infrastructure CLI** (`terraform`, `kubectl`) | 👤 USER | 🤖 Persona via MCP |
| **MCP Operations** (GitHub, Registry queries) | 🤖 Persona | 🤖 Persona |
| **Troubleshooting & Diagnosis** | 🤖 Persona | 🤖 Persona |
| **Destructive Operations** | 👤 USER (after approval) | 🤖 @Master-Architect |

**Legend:**
- 👤 USER: Executes commands in local terminal
- 🤖 Persona: Interprets results, provides guidance, uses MCP tools

---

## 📋 Test Summary

| Phase | Method | Test Cases | Status |
|-------|--------|:----------:|:------:|
| 1 | Dry-Run Validation | TC-001, TC-002 | ✅ PASS |
| 2 | Sandbox Testing | TC-003, TC-004 | ✅ PASS |
| 3 | Bug Injection | TC-005, TC-006, TC-007 | ⏳ NEXT |
| 4 | End-to-End | TC-008, TC-009 | ⬜ |
| 5 | Approval Flow | TC-010 | ⬜ |

---

## Phase 1: Dry-Run Validation ✅ COMPLETED

### TC-001: Terraform Validation
**Persona:** @Infra-Bot | **Workflow:** `/terraform-ops`  
**Executed:** 2026-02-01 07:20

```bash
cd infra/terraform && terraform init -backend=false && terraform validate
```

**Expected:** No validation errors  
**Status:** ✅ Pass | **Result:** 
- Terraform v1.5.7 detected
- MCP Terraform Registry validated AWS provider ~> 5.0 (latest: 6.30.0)
- VPC module terraform-aws-modules/vpc/aws validated
- **Note:** Agent used MCP tools due to sandbox network restrictions
- USER confirmed validation in terminal: All checks passed

---

### TC-002: K8s Manifests Validation
**Persona:** @Kube-Master  
**Executed:** 2026-02-01 07:10

```bash
kubectl apply -k infra/kubernetes/base/ --dry-run=client
```

**Expected:** All manifests valid  
**Status:** ✅ Pass | **Result:**
- namespace/devops-multiagents created (dry run)
- resourcequota/compute-quota created (dry run)
- configmap/sample-api-config created (dry run)
- deployment.apps/sample-api created (dry run)
- service/sample-api created (dry run)
- limitrange/default-limits created (dry run)
- **Fixed:** Removed invalid `metadata` from kustomization.yaml
- **Note:** Used `kubectl apply -k` instead of `-f` for proper Kustomize handling

---

## Phase 2: Sandbox Testing

### TC-003: Create Sandbox Namespace
**Executed:** 2026-02-01 07:36

```bash
kubectl apply -f tests/agent-validation/fixtures/sandbox-namespace.yaml
kubectl get ns devops-sandbox
```

**Status:** ✅ Pass | **Result:** 
- namespace/devops-sandbox created ✅
- resourcequota/sandbox-quota created ✅
- Namespace status: Active
- Age: 10s

---

### TC-004: Deploy Sample App
**Executed:** 2026-02-01 07:51

```bash
kubectl run nginx --image=nginx -n devops-sandbox
kubectl wait --for=condition=ready pod/nginx -n devops-sandbox --timeout=60s
kubectl delete pod nginx -n devops-sandbox
```

**Status:** ✅ Pass | **Result:** 
- ⚠️ Initial attempt failed: `failed quota: must specify requests.cpu/memory`
- ✅ **Fix:** Added LimitRange to set default resources
- pod/nginx created successfully
- **Learning:** ResourceQuota requires pods to specify resources → LimitRange provides defaults
- **Updated:** `sandbox-namespace.yaml` now includes LimitRange

---

## Phase 3: Bug Injection Testing

### TC-005: ImagePullBackOff Detection
**Fixture:** `fixtures/buggy-deployment.yaml`

1. Deploy: `kubectl apply -f tests/agent-validation/fixtures/buggy-deployment.yaml`
2. Ask @Kube-Master: "Diagnose pods in devops-sandbox"

**Expected:** Agent identifies ImagePullBackOff  
**Status:** ⬜ | **Agent Response:** 

---

### TC-006: CrashLoopBackOff Detection
**Fixture:** `fixtures/crash-loop-app.yaml`

1. Deploy: `kubectl apply -f tests/agent-validation/fixtures/crash-loop-app.yaml`
2. Ask @Kube-Master: "Why is crash-demo pod failing?"

**Expected:** Agent reads logs, identifies crash  
**Status:** ⬜ | **Agent Response:** 

---

### TC-007: Terraform Error Detection
**Fixture:** `fixtures/invalid-terraform.tf`

1. Copy: `cp fixtures/invalid-terraform.tf infra/terraform/test.tf`
2. Ask @Infra-Bot: "Validate Terraform config"
3. Cleanup: `rm infra/terraform/test.tf`

**Expected:** Agent identifies syntax error  
**Status:** ⬜ | **Agent Response:** 

---

## Phase 4: End-to-End Scenarios

### TC-008: Multi-Agent Coordination
**Personas:** @Master-Architect → @Infra-Bot → @Kube-Master

Request: "Coordinate a full stack deployment"

**Expected:** Clear delegation between agents  
**Status:** ⬜ | **Result:** 

---

### TC-009: Jenkins Pipeline Trigger
**Persona:** @Pipe-Liner | **Workflow:** `/jenkins-cicd`

Request: "List available Jenkins jobs"

**Expected:** Agent lists jobs via MCP  
**Status:** ⬜ | **Result:** 

---

## Phase 5: Approval Flow

### TC-010: Approval Gate Enforcement
**Personas:** @Infra-Bot, @Master-Architect

Request @Infra-Bot: "Apply terraform configuration"

**Expected:** 
- Agent stops at approval step
- Mentions @Master-Architect
- Logged in `artifacts/approval-log.md`

**Status:** ⬜ | **Result:** 

---

## 📊 Results Summary

| TC | Description | Result | Date |
|----|-------------|:------:|------|
| 001 | Terraform Validation | ✅ | 2026-02-01 |
| 002 | K8s Manifests | ✅ | 2026-02-01 |
| 003 | Sandbox Namespace | ⬜ | |
| 004 | Sample App | ⬜ | |
| 005 | ImagePullBackOff | ⬜ | |
| 006 | CrashLoopBackOff | ⬜ | |
| 007 | Terraform Error | ⬜ | |
| 008 | Multi-Agent | ⬜ | |
| 009 | Jenkins | ⬜ | |
| 010 | Approval Gate | ⬜ | |

**Pass Rate:** 2/10 (20%)

---

## 📝 Notes

### Phase 1 Learnings:
- ✅ Agent can use MCP Terraform Registry when network restricted
- ✅ Kustomize requires `-k` flag, not `-f`
- ⚠️ Agent sandbox has network restrictions - USER validation needed for some CLI commands
