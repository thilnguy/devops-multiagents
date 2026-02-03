---
description: GitHub workflow for PR reviews, issues, and repository management
---

# GitHub Operations Workflow

This workflow enables automated GitHub interactions for code and project management.

## Persona
- **Master Architect**: Primary executor

## MCP Tools Used
- `mcp_github_list_pull_requests`
- `mcp_github_get_pull_request`
- `mcp_github_create_pull_request_review`
- `mcp_github_list_issues`
- `mcp_github_create_issue`

## Steps

### Pull Request Management
*Skill Used: `mcp-github-flow`*

> @Master-Architect: Ensure all Pull Requests are reviewed and processed according to project standards.

```
mcp_github_list_pull_requests with owner="<ORG>" repo="devops_multiagents" state="open"
```

#### Get PR Details

```
mcp_github_get_pull_request with owner="<ORG>" repo="devops_multiagents" pull_number=<PR_NUMBER>
```

#### Get PR Files Changed

```
mcp_github_get_pull_request_files with owner="<ORG>" repo="devops_multiagents" pull_number=<PR_NUMBER>
```

#### Review a PR

Approve:
```
mcp_github_create_pull_request_review with owner="<ORG>" repo="devops_multiagents" pull_number=<PR_NUMBER> body="LGTM! All checks pass." event="APPROVE"
```

Request changes:
```
mcp_github_create_pull_request_review with owner="<ORG>" repo="devops_multiagents" pull_number=<PR_NUMBER> body="Please fix the issues mentioned." event="REQUEST_CHANGES"
```

### Issue Management
*Skill Used: `mcp-github-flow`*

> @Master-Architect: Ensure incoming issues are triaged, labeled, and prioritized effectively.

```
mcp_github_list_issues with owner="<ORG>" repo="devops_multiagents" state="open"
```

#### Create Issue

```
mcp_github_create_issue with owner="<ORG>" repo="devops_multiagents" title="Bug: Pod restart loop" body="## Description\nPods are restarting frequently.\n\n## Steps to Reproduce\n1. Deploy application\n2. Wait 5 minutes\n\n## Expected Behavior\nPods should remain stable." labels=["bug", "kubernetes"]
```

#### Update Issue

```
mcp_github_update_issue with owner="<ORG>" repo="devops_multiagents" issue_number=<ISSUE_NUMBER> state="closed"
```

### Branch Management

#### Create Feature Branch

```
mcp_github_create_branch with owner="<ORG>" repo="devops_multiagents" branch="feature/new-deployment" from_branch="main"
```

### Repository Operations

#### Get File Contents

```
mcp_github_get_file_contents with owner="<ORG>" repo="devops_multiagents" path="README.md"
```

#### Push File Changes

```
mcp_github_push_files with owner="<ORG>" repo="devops_multiagents" branch="feature/update-docs" files=[{"path": "docs/update.md", "content": "# Updated Content"}] message="docs: update documentation"
```

## PR Review Guidelines

When reviewing PRs:

1. **Check CI Status**: Ensure all checks pass
2. **Review Changes**: Focus on logic, security, performance
3. **Test Coverage**: Verify tests exist for new code
4. **Documentation**: Update docs if needed

## Automated PR Workflow

```
1. List open PRs
2. For each PR without review:
   a. Get PR details and files
   b. Analyze changes
   c. Check for security issues
   d. Verify test coverage
   e. Create review with feedback
```

## Issue Triage Workflow

```
1. List new issues (unlabeled)
2. Analyze issue content
3. Add appropriate labels:
   - bug / feature / enhancement
   - priority: critical / high / medium / low
   - component: terraform / kubernetes / jenkins
4. Assign to appropriate persona
```
