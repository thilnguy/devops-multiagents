# Infrastructure Cost Optimization - Walkthrough

**Date:** 2026-02-04  
**Status:** ✅ Complete

---

## Overview

This document covers the infrastructure cost optimization implemented for the DevOps Multi-Agent Ecosystem, focusing on reducing cloud spend while maintaining reliability.

---

## 1. Strategy: "Stable Prod - Austere Non-Prod"

| Aspect | Non-Prod (Dev/Staging) | Production |
|:---|:---|:---|
| **Compute** | Spot Instances (~70% savings) | On-Demand (stability) |
| **Architecture** | ARM64 (Graviton) | ARM64 (Graviton) |
| **NAT Gateway** | Single (saves ~$60/mo) | Multi-AZ (high availability) |
| **Flow Logs** | Disabled (cost) | Enabled (audit) |
| **Node Scaling** | min=1, max=3 | min=2, max=5 |

---

## 2. Terraform Implementation

### Files Created/Modified

| File | Purpose |
|:---|:---|
| [eks.tf](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/terraform/eks.tf) | EKS module with ARM64 AMI and dynamic Spot/On-Demand |
| [terraform.nonprod.tfvars](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/terraform/terraform.nonprod.tfvars) | Austere config: Spot, single NAT |
| [terraform.prod.tfvars](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/terraform/terraform.prod.tfvars) | Stable config: On-Demand, multi-NAT |
| [Makefile](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/terraform/Makefile) | Enforces correct `-var-file` usage |

### Key Config: VPC NAT Gateway Logic
```hcl
# main.tf (lines 82-84)
enable_nat_gateway     = true
single_nat_gateway     = var.environment != "production"
one_nat_gateway_per_az = var.environment == "production"
```

### Key Config: EKS Node Group
```hcl
# eks.tf
instance_types = var.eks_node_group_instance_types  # t4g.medium / m6g.large
capacity_type  = var.eks_node_group_capacity_type   # SPOT / ON_DEMAND
ami_type       = "AL2023_ARM_64_STANDARD"           # Graviton
```

---

## 3. Kubernetes Namespace Isolation

Merged Dev/Staging into single Non-Prod cluster with namespace isolation.

| Resource | File |
|:---|:---|
| Dev Namespace | [ns-dev.yaml](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/kubernetes/namespaces/ns-dev.yaml) |
| Staging Namespace | [ns-staging.yaml](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/kubernetes/namespaces/ns-staging.yaml) |
| Dev Quota | [dev-quota.yaml](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/kubernetes/quotas/dev-quota.yaml) |
| Staging Quota | [staging-quota.yaml](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/infra/kubernetes/quotas/staging-quota.yaml) |

**Quota Config (Dev):**
- CPU: 2 requests / 4 limits
- Memory: 4Gi requests / 8Gi limits
- Pods: 10 max

---

## 4. Policy Guard (Regression Prevention)

| File | Purpose |
|:---|:---|
| [validate_infra_policies.py](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/tests/scripts/validate_infra_policies.py) | Policy-as-Code validator |
| [Jenkinsfile](file:///Users/lananh/Workspace/code/MyAGWorkspace/devops_multiagents/pipelines/jenkins/Jenkinsfile) | Pipeline with Policy Gate stage |

**Rules Enforced:**
- Non-Prod: Must use SPOT, ARM64, Single NAT
- Prod: Must use ON_DEMAND, Multi-AZ NAT

---

## 5. Estimated Savings

| Category | Monthly Savings |
|:---|---:|
| Spot vs On-Demand (Dev) | ~$50-80 |
| Single NAT (Dev) | ~$60 |
| Cluster Consolidation | ~$73 |
| ARM64 vs x86 | ~15% |
| **Total (Non-Prod)** | **~$180-220/mo** |

---

## 6. Usage

```bash
# Plan for Dev (uses terraform.nonprod.tfvars)
cd infra/terraform
make plan-dev

# Validate policies
make validate ENV=dev

# Apply
make apply
```
