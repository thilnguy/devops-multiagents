# Infrastructure Cost Optimization Guide (Phase 2)

This guide details the implementation of the **"Prod Stable - Non-Prod Austere"** strategy to reduce infrastructure costs by ~60-70%.

## 📉 Strategy Overview

| Feature | Non-Prod (Dev/Staging) | Production |
|:---|:---|:---|
| **Cluster** | Shared EKS Cluster | Isolated EKS Cluster |
| **Compute** | **Spot Instances** (100%) | **On-Demand** (Reserved/Savings Plan) |
| **Architecture** | **ARM64** (Graviton `t4g.medium`) | **ARM64** (Graviton `m6g.large`) |
| **Network** | Single NAT Gateway | Multi-AZ (2) NAT Gateways |
| **Storage** | Single-AZ Database | Single-AZ + Automated Backups |

## 🛠️ Implementation Details

### 1. Terraform Configuration using `.tfvars`

We have introduced environment-specific variable files to enforce these strategies.

#### Deploying Non-Prod (Dev & Staging)
Use `terraform.nonprod.tfvars` to deploy the shared cluster with cost-saving settings.

```bash
cd infra/terraform
terraform init
terraform plan -var-file="terraform.nonprod.tfvars" -out=nonprod.plan
terraform apply "nonprod.plan"
```

**Key Settings applied:**
- `capacity_type = "SPOT"`
- `instance_types = ["t4g.medium"]`
- `nat_gateway_count = 1`

#### Deploying Production
Use `terraform.prod.tfvars` to deploy for the stable, high-performance environment.

```bash
cd infra/terraform
terraform init
terraform plan -var-file="terraform.prod.tfvars" -out=prod.plan
terraform apply "prod.plan"
```

**Key Settings applied:**
- `capacity_type = "ON_DEMAND"`
- `instance_types = ["m6g.large"]`
- `nat_gateway_count = 2`

### 2. Kubernetes Namespace Isolation

Since Dev and Staging share the **Non-Prod** cluster, we use Namespaces and ResourceQuotas to isolate them.

**Manifests:**
- `infra/kubernetes/namespaces/ns-dev.yaml`
- `infra/kubernetes/namespaces/ns-staging.yaml`
- `infra/kubernetes/quotas/dev-quota.yaml` (Low limits)
- `infra/kubernetes/quotas/staging-quota.yaml` (Medium limits)

**Apply Configuration:**
```bash
kubectl apply -f infra/kubernetes/namespaces/
kubectl apply -f infra/kubernetes/quotas/
```

## ✅ Verification Checklist

1.  **Check Nodes**: Ensure nodes are running on ARM64 architecture.
    ```bash
    kubectl get nodes -L kubernetes.io/arch
    # Should show 'arm64'
    ```
2.  **Check Spot Instances**: Verification via AWS Console or CLI.
    kubectl describe quota -n ns-dev
    ```

## 🛡️ Policy Validation (Guardrails)

To avoid infrastructure regressions (e.g., someone accidentally deploying On-Demand in Dev), we have implemented a validation script.

**How to run locally:**
```bash
# 1. Initialize and generate plan
cd infra/terraform
terraform init
terraform plan -var-file="terraform.nonprod.tfvars" -out=tfplan

# 2. Convert plan to JSON
terraform show -json tfplan > tfplan.json

# 3. Run Policy Validator
python3 ../../tests/scripts/validate_infra_policies.py tfplan.json --env dev
```
