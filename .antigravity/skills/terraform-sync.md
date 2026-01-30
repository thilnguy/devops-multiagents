---
name: Terraform Sync
description: Skill to synchronize infrastructure state using Terraform
---

# Skill: Terraform Sync (Drift Remediation)

**Context:** Use this when @Infra-Bot needs to align the actual infrastructure with the configuration files, typically after a Drift is detected.

## Steps
1.  **Plan First:** Always execute `terraform plan` first (see `terraform-plan.md`) to visualize what will change.
2.  **Verify:** Check if the plan matches the intended state. If `terraform plan` shows changes that are unexpected (drift), analyze why.
3.  **Approve:** Ask the user for explicit approval to apply changes.
4.  **Apply:** Run `terraform apply` (via `run_command`).
    - Use `-auto-approve` ONLY if the user has explicitly authorized it for this session or if running in a non-interactive automation workflow approved by the Master Architect.
5.  **Confirm:** Check the output to ensure the Apply was successful.
