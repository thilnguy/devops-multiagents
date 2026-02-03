---
name: Terraform Plan
description: Instructions for checking infrastructure changes using Terraform
---

# Skill: Terraform Planning

**Context:** Use this skill when you need to change infrastructure or verify the current state against the desired state.

## Steps
1.  **Navigate:** Ensure you are in the correct directory containing Terraform configuration (usually `infra/terraform/...`).
2.  **Init (if needed):** If the directory hasn't been initialized, check for `.terraform` or run an init command (via `run_command` with `terraform init` or equivalent MCP tool).
3.  **Validate:** Run `terraform validate` to ensure configuration syntax is correct.
4.  **Plan:** Use the `run_command` tool to execute `terraform plan`.
    - *Note:* If a Terraform MCP server is active, checking for available resources using `mcp_terraform-registry_listDataSources` or similar might be useful for discovery, but `terraform plan` is the definitive check.
4.  **Analyze:** Review the output for:
    - **Additions:** New resources to be created.
    - **Changes:** Modifications to existing resources (check for destructive changes!).
    - **Deletions:** Resources to be removed.
5.  **Report:** Summarize the plan to the user/Master Architect before asking for approval to apply.
