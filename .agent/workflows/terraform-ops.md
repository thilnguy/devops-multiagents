---
description: Plan and apply Terraform infrastructure changes safely
---

# Terraform Operations Workflow

This workflow guides the Infra Bot through safe Terraform operations.

## Persona
- **Infra Bot**: Primary executor

## MCP Tools Used
- `mcp_terraform-registry_providerDetails`
- `mcp_terraform-registry_resourceArgumentDetails`
- `mcp_terraform-registry_moduleDetails`

## Steps

### Step 1: Pre-flight Checks

// turbo
```bash
terraform --version
```

// turbo
```bash
aws sts get-caller-identity
```

### Step 2: Initialize Terraform
*Skill Used: `terraform-plan`*

> @Infra-Bot: Ensure the Terraform working directory is initialized and ready for planning.

Navigate to terraform directory:
```bash
cd infra/terraform
```

Initialize (fresh clone or module updates):
// turbo
```bash
terraform init -upgrade
```

### Step 3: Validate Configuration

// turbo
```bash
terraform validate
```

// turbo
```bash
terraform fmt -check -recursive
```

### Step 4: Generate Plan

For review:
```bash
terraform plan -out=changes.tfplan
```

Review plan output for:
- `+` resources to add
- `~` resources to modify
- `-` resources to destroy

**STOP if any unexpected destroys are shown!**

### Step 5: Apply Changes
*Skill Used: `terraform-sync`*

> @Infra-Bot: Synchronize infrastructure state by applying the approved plan.

> [!CAUTION]
> ⚠️ **REQUIRES APPROVAL** - This step modifies infrastructure.
> Request approval from @Master-Architect before proceeding in production.

Apply with the saved plan:
```bash
terraform apply changes.tfplan
```

### Step 6: Capture Outputs

// turbo
```bash
terraform output
```

Save for other agents:
// turbo
```bash
terraform output -json > ../outputs/terraform-outputs.json
```

### Step 7: State Management

Check state:
// turbo
```bash
terraform state list
```

If drift detected:
```bash
terraform refresh
```

## Module Research (Using MCP)

To find modules:
```
mcp_terraform-registry_moduleSearch with query="vpc" provider="aws"
```

To get module details:
```
mcp_terraform-registry_moduleDetails with namespace="terraform-aws-modules" module="vpc" provider="aws"
```

To understand resource arguments:
```
mcp_terraform-registry_resourceArgumentDetails with provider="aws" namespace="hashicorp" resource="aws_instance"
```

## Safety Rules

1. **Never apply without a plan file in production**
2. **Always backup state before risky operations**
3. **Use workspaces for environment separation**
4. **Lock state during apply operations**

## Rollback

If apply fails mid-way:
```bash
terraform state list
terraform state rm <PARTIALLY_CREATED_RESOURCE>
terraform apply
```
