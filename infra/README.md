# 🏗️ Infrastructure as Code (IaC)

This directory contains the declarative infrastructure definitions managed by the **Infra Bot** and **Kube Master** agents.

## Structure

### 1. Terraform (`/terraform`)
Managed by **Infra Bot**. Defines the cloud resources and provisioning logic.

*   `main.tf`: Core resource definitions.
*   `variables.tf`: Input variable declarations.
*   `outputs.tf`: Output values (e.g., K8s endpoint, VPC IDs).
*   `versions.tf`: Provider version constraints.

**Usage:**
```bash
cd terraform
terraform init
terraform plan
```

### 2. Kubernetes (`/kubernetes`)
Managed by **Kube Master**. Defines the workload manifests and configuration.

*   `deployment.yaml`: Application deployment definitions.
*   `service.yaml`: Network exposure and load balancing.
*   `configmap.yaml`: Configuration injection.
*   `kustomization.yaml`: Kustomize overlay management.

**Usage:**
```bash
kubectl apply -f kubernetes/
# or
kubectl apply -k kubernetes/
```

## Agent Workflows
*   **Provisioning:** Infra Bot executes Terraform plans to stand up the cluster.
*   **Deployment:** Kube Master applies manifests to the provisioned cluster.
*   **Drift Detection:** Watchdog monitors state vs. definition.
