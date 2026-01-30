# DevOps Multi-Agent Ecosystem

A multi-agent system for automating DevOps tasks using AI-powered personas and MCP (Model Context Protocol) integrations.

## Quick Start

### 1. Prerequisites
- Python 3.8+
- Node.js 18+
- Terraform 1.0+
- kubectl configured
- Jenkins (optional)

### 2. Configure MCP Servers
Edit `~/.gemini/antigravity/mcp_config.json` and fill in your credentials:
```json
{
  "mcpServers": {
    "github": { "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token" }},
    "jenkins": { "env": { "JENKINS_URL": "https://...", "JENKINS_API_TOKEN": "..." }}
  }
}
```

### 3. Verify Ecosystem
```bash
# Check logical consistency
python3 tests/validate_ecosystem.py

# Check MCP server health
python3 .antigravity/scripts/mcp-health-check.py
```

## Architecture

| Persona | Role | Skills |
|---------|------|--------|
| **Master Architect** | System Orchestrator | Strategic planning |
| **Infra Bot** | IaC Specialist | `terraform-plan`, `terraform-sync` |
| **Kube Master** | K8s Expert | `k8s-troubleshoot` |
| **Pipe Liner** | CI/CD Automation | `jenkins-ops` |

## Directory Structure
```
.antigravity/
├── personas/       # Agent definitions
├── skills/         # Capability definitions
└── scripts/        # Utility scripts

infra/
├── terraform/      # IaC configurations
└── kubernetes/     # K8s manifests

pipelines/
└── jenkins/        # Jenkinsfile

tests/              # Validation scripts
```

## MCP Servers
- **GitHub** - Repository management
- **Terraform Registry** - IaC resources
- **Kubernetes** - Cluster operations
- **Jenkins** - CI/CD orchestration
- **Fetch** - Documentation retrieval

## CI/CD Pipeline
The Jenkinsfile in `pipelines/jenkins/` runs:
1. **Validate**: Terraform fmt/validate, K8s lint
2. **Test**: Ecosystem validation
3. **Plan**: Terraform plan (main branch)
4. **Deploy**: Manual approval gate

## License
MIT
