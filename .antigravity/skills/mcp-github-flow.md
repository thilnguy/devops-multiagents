---
name: GitHub Flow
description: Manage GitHub repositories, PRs, and issues
---

# Skill: GitHub Managed Workflow

**Context:** Use this when interacting with GitHub repositories, Pull Requests, or Issues.

## Required MCP Server
- `github` (provides `create_issue`, `create_pull_request`, `push_files`, etc.)

## Workflow

### 1. Check Repository State
- Use `mcp_github_get_file_contents` to verify current branch state.

### 2. Execute Changes
- **Bug Fix:** Create an issue first with `mcp_github_create_issue` to track.
- **After coding:** Use `mcp_github_create_branch` -> `mcp_github_push_files` -> `mcp_github_create_pull_request`.

### 3. PR Standards
- PR body must include a summary of files changed.
- @mention relevant Personas for review.