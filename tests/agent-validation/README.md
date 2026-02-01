# 🧪 Agent Testing Plan

## Overview
This directory contains test scenarios, fixtures, and results for validating the DevOps Multi-Agent System.

## Directory Structure
```
tests/agent-validation/
├── README.md                    # This file
├── test-plan.md                 # Master test plan with all scenarios
├── fixtures/                    # Test data and buggy apps
│   ├── sandbox-namespace.yaml
│   ├── buggy-deployment.yaml
│   ├── crash-loop-app.yaml
│   └── invalid-terraform.tf
└── results/                     # Test execution logs
```

## Quick Start

### Phase 1: Dry-Run Validation
```bash
cd infra/terraform && terraform validate
kubectl apply -f infra/kubernetes/base/ --dry-run=client
```

### Phase 2: Sandbox Testing
```bash
kubectl apply -f tests/agent-validation/fixtures/sandbox-namespace.yaml
kubectl apply -f tests/agent-validation/fixtures/buggy-deployment.yaml
```

### Phase 3: Run Scenarios
Follow test cases in `test-plan.md`
