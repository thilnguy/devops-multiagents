---
name: Jenkins Ops
description: Manage Jenkins builds and monitor job status
---

# Skill: Jenkins Ops

**Context:** Use this when @Pipe-Liner needs to interact with Jenkins for build triggers, status checks, or job management.

## Capabilities
1.  **Trigger Build:** Start a Jenkins job with specific parameters.
2.  **Monitor Status:** Check the current state of a build (Running, Success, Failure).
3.  **Retrieve Logs:** Get build logs to diagnose failures.

## Workflow
1.  **Identify Job:** Determine the correct Jenkins job name.
2.  **Check Previous State:** View the last build status for baseline.
3.  **Trigger:** Use `jenkins-mcp-server` tools to start the build.
4.  **Poll:** Periodically check build status until completion.
5.  **Report:** Inform the Master Architect or user of the result.
