---
description: Full infrastructure provisioning with Terraform and K8s deployment
---

# End-to-End Infrastructure Deployment Workflow

This workflow orchestrates a complete deployment from infrastructure provisioning to application deployment.

## Personas Involved
- **Master Architect**: Orchestrates the overall flow
- **Infra Bot**: Handles Terraform operations
- **Kube Master**: Manages Kubernetes deployment

## Prerequisites
- AWS credentials configured
- Kubernetes cluster accessible
- Terraform CLI installed

## Steps

### Phase 1: Infrastructure Planning (Infra Bot)
*Skill Used: `terraform-plan`*

> @Infra-Bot: Ensure infrastructure changes are identified and planned for review.
```bash
cd infra/terraform
```

2. Initialize Terraform:
// turbo
```bash
terraform init -backend=false
```

3. Validate configuration:
// turbo
```bash
terraform validate
```

4. Generate execution plan:
```bash
terraform plan -out=deploy.tfplan
```

5. Review the plan output for:
   - Resources to be created
   - Any destructive changes
   - Cost implications

### Phase 2: Infrastructure Apply (Infra Bot)

> @Infra-Bot: Execute the approved infrastructure changes.

> [!CAUTION]
> ⚠️ **REQUIRES APPROVAL** - Destructive operation. Request approval from @Master-Architect before proceeding.

6. Apply the Terraform plan:
```bash
terraform apply deploy.tfplan
```

7. Capture outputs for Kubernetes:
// turbo
```bash
terraform output -json > /tmp/tf-outputs.json
```

### Phase 3: Kubernetes Deployment (Kube Master)
*Skill Used: `k8s-troubleshoot` (includes apply)*

> @Kube-Master: Ensure application components are correctly deployed to the cluster.
```bash
cd infra/kubernetes/base
```

9. Create namespace first:
// turbo
```bash
kubectl apply -f namespace.yaml
```

10. Deploy ConfigMap:
// turbo
```bash
kubectl apply -f configmap.yaml
```

11. Deploy application:

> [!IMPORTANT]
> For production: Request approval from @Master-Architect first.

```bash
kubectl apply -f deployment.yaml
```

12. Create service:
// turbo
```bash
kubectl apply -f service.yaml
```

13. Verify deployment status:
// turbo
```bash
kubectl get pods -n devops-multiagents -w --timeout=120s
```

### Phase 4: Validation (Master Architect)

> @Master-Architect: Validate the deployment health and check for any runtime errors.
// turbo
```bash
kubectl get all -n devops-multiagents
```

15. Check pod logs for errors:
// turbo
```bash
kubectl logs -l app=sample-api -n devops-multiagents --tail=50
```

## Rollback Procedure

If deployment fails:
```bash
kubectl rollout undo deployment/sample-api -n devops-multiagents
```

## Success Criteria
- All pods in Running state
- Service endpoints available
- Health check passing
