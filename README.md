# 🤖 DevOps Multi-Agent Ecosystem

![System Status](https://img.shields.io/badge/System-Production%20Ready-success)
![Maturity](https://img.shields.io/badge/Maturity-v2.1-blue)
![Agents](https://img.shields.io/badge/Agents-Autonomous-purple)

**A next-generation DevOps automation platform powered by multiple specialized AI Agents collaborating via the Model Context Protocol (MCP).**

## 📖 Overview

The **DevOps Multi-Agent Ecosystem** replaces monolithic automation scripts with a team of distinct AI personas. Each agent possesses specialized "skills" (Terraform, Kubernetes, Jenkins, GitHub) and adheres to strict security boundaries. They collaborate to plan, deploy, monitor, and heal infrastructure.

### 🌟 Key Features
*   **Role-Based AI Personas:** Specialized agents for Architecture, Infrastructure, K8s, and CI/CD.
*   **MCP Integration:** Seamless connection to external tools (GitHub, Jenkins, K8s) via standardized protocol.
*   **Self-Healing Infrastructure:** Autonomous Watchdog agents detect and propose fixes for drift and errors.
*   **Tiered Validation:** Comprehensive testing strategy from smoke tests to deep cognitive audits.
*   **Security First:** Strict approval gates and persona-based permission boundaries.

---

## 🏗️ Architecture

| Persona | Role | Responsibilities | Tools (MCP) |
|:---:|:---|:---|:---|
| 🧠 | **Master Architect** | Orchestration, Strategy, Integration | GitHub, Planning |
| 🏗️ | **Infra Bot** | Infrastructure as Code (IaC) | Terraform, AWS |
| ☸️ | **Kube Master** | Container Orchestration | Kubernetes, Helm |
| 🚀 | **Pipe Liner** | CI/CD & Release Management | Jenkins |
| 👁️ | **Watchdog** | Observability & Security | Logs, Metrics |
| ⚖️ | **Arbitrator** | Conflict Resolution | Policy Enforcement |

---

## 🚀 Getting Started

### Prerequisites
*   **Python:** 3.8+
*   **Terraform:** 1.0+
*   **Kubernetes:** `kubectl` configured with access to a cluster (e.g., Docker Desktop).
*   **Node.js:** 18+ (for some tool dependencies).

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/thilnguy/devops-multiagents.git
    cd devops-multiagents
    ```

2.  **Configure Environment**
    Copy the example configuration and fill in your credentials.
    ```bash
    cp .env.example .env
    ```
    > **Note:** Ensure you configure your `ANTIGRAVITY_MCP_CONFIG` or local MCP settings for GitHub and Jenkins access.

3.  **Verify Setup**
    Run the ecosystem validator to check dependencies.
    ```bash
    python3 tests/validate_ecosystem.py
    ```

---

## 🧪 Validation & Testing

We employ a **Hybrid Execution Model** combining local CLI execution with Agent cognition.

| Tier | Command | Description | Time |
|---|---|---|---|
| **Quick** | `/agent-validation-quick` | Smoke test for core syntax & drift detection. | ~30s |
| **Standard** | `/agent-validation-standard` | Daily checks including MCP connectivity. | ~3m |
| **Deep** | `/agent-validation-deep` | Full release audit, security & persona bounds. | ~10m |

👉 **[See Detailed Testing Documentation](tests/README.md)**

---

## 📂 Project Structure

```text
.
├── .agent/                 # Agent workflows and definitions
│   └── workflows/          # Automation workflows (Quick, Standard, Deep)
├── .antigravity/           # Framework configuration & state
├── artifacts/              # Generated logs, plans, and persistent data
├── docs/                   # Detailed documentation
├── infra/                  # Infrastructure as Code
│   ├── k8s/                # Kubernetes manifests
│   └── terraform/          # Terraform modules
├── pipelines/              # CI/CD definitions (Jenkinsfile)
└── tests/                  # Validation suites & scripts
    ├── results/            # generated validation reports
    └── scripts/            # hybrid execution scripts
```

---

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-agent`).
3.  Run the **Quick Validation** (`/agent-validation-quick`) to ensure stability.
4.  Commit changes and open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
