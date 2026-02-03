---
description: Trigger, monitor, and manage Jenkins CI/CD builds
---

# Jenkins CI/CD Pipeline Workflow

This workflow guides the Pipe Liner persona through Jenkins operations.

## Persona
- **Pipe Liner**: Primary executor

## MCP Tools Used
- `mcp_jenkins_getJobs`
- `mcp_jenkins_triggerBuild`
- `mcp_jenkins_getBuild`
- `mcp_jenkins_getQueueItem`

## Prerequisites
- Jenkins URL configured in environment
- API Token available
- Pipeline job exists

## Steps

### Step 1: List Available Jobs
*Skill Used: `jenkins-ops`*

> @Pipe-Liner: Ensure visibility of available CI/CD pipelines.

Using MCP:
```
mcp_jenkins_getJobs
```

Or with parent folder:
```
mcp_jenkins_getJobs with parentFullName="DevOps"
```

### Step 2: Check Job Status

Get job details:
```
mcp_jenkins_getJob with jobFullName="DevOps/multiagent-deploy"
```

### Step 3: Trigger a Build
*Skill Used: `jenkins-ops`*

> @Pipe-Liner: Trigger and oversee the execution of the build pipeline.

Without parameters:
```
mcp_jenkins_triggerBuild with jobFullName="DevOps/multiagent-deploy" parameters={}
```

With parameters:
```
mcp_jenkins_triggerBuild with jobFullName="DevOps/multiagent-deploy" parameters={"ENVIRONMENT": "staging", "DEPLOY_K8S": "true"}
```

### Step 4: Monitor Build Queue

Check if build started:
```
mcp_jenkins_getQueueItem with queueId=<QUEUE_ID>
```

### Step 5: Get Build Status

Check latest build:
```
mcp_jenkins_getBuild with jobFullName="DevOps/multiagent-deploy"
```

Check specific build:
```
mcp_jenkins_getBuild with jobFullName="DevOps/multiagent-deploy" buildNumber=42
```

### Step 6: Review Artifacts

List build artifacts:
```
mcp_jenkins_listBuildArtifacts with jobFullName="DevOps/multiagent-deploy"
```

Read specific artifact:
```
mcp_jenkins_readBuildArtifact with jobFullName="DevOps/multiagent-deploy" artifactPath="reports/test-results.xml"
```

### Step 7: Handle Failures

If build fails:

1. Check console output for errors
2. Identify failing stage
3. Review test results artifacts
4. Escalate to Master Architect if infrastructure issue

Stop a running build:
```
mcp_jenkins_stopBuild with jobFullName="DevOps/multiagent-deploy"
```

Cancel queued build:
```
mcp_jenkins_cancelQueuedBuild with jobFullName="DevOps/multiagent-deploy"
```

## Common Build Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| ENVIRONMENT | dev/staging/prod | Target environment |
| DEPLOY_K8S | true/false | Deploy to Kubernetes |
| RUN_TESTS | true/false | Execute test suite |
| TERRAFORM_APPLY | true/false | Apply infra changes |

## Automation Tips

1. **Parallel Builds**: Check queue before triggering to avoid overload
2. **Build Chaining**: Use build completion status to trigger next stage
3. **Artifact Passing**: Save outputs as artifacts for downstream jobs
