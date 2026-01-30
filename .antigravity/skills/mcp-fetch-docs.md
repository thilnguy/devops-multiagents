---
name: MCP Fetch Docs
description: Retrieve external documentation using MCP Fetch server
---

# Skill: Live Documentation Fetching

**Context:** Use this when needing up-to-date documentation or examples from external sources.

## Required MCP Server
- `mcp-fetch` (provides `get_markdown`, `get_markdown_summary`, `get_raw_text`)

## Workflow

### 1. Identify Documentation URL
- Locate the official documentation page for the technology in question.
- Example: `https://kubernetes.io/docs/concepts/`

### 2. Fetch Content
- Use `mcp_mcp-fetch_get_markdown` to retrieve the page as Markdown.
- For summaries, use `mcp_mcp-fetch_get_markdown_summary`.

### 3. Extract Examples
- Parse the returned Markdown for code blocks.
- Apply relevant examples to the current project.

### 4. Cite Sources
- Always add a comment in the code citing the documentation URL.
- Example: `# Ref: https://kubernetes.io/docs/...`