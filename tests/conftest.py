"""
Pytest configuration and shared fixtures for DevOps Multi-Agent tests.
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def personas_dir(project_root):
    """Return the personas directory."""
    return project_root / ".antigravity" / "personas"


@pytest.fixture(scope="session")
def skills_dir(project_root):
    """Return the skills directory."""
    return project_root / ".antigravity" / "skills"


@pytest.fixture(scope="session")
def terraform_dir(project_root):
    """Return the Terraform directory."""
    return project_root / "infra" / "terraform"


@pytest.fixture(scope="session")
def k8s_dir(project_root):
    """Return the Kubernetes directory."""
    return project_root / "infra" / "kubernetes" / "base"


@pytest.fixture(scope="session")
def mcp_config():
    """Load and return MCP configuration."""
    config_path = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


@pytest.fixture(scope="session")
def mcp_servers(mcp_config):
    """Return list of configured MCP servers."""
    return list(mcp_config.get("mcpServers", {}).keys())


# Markers for conditional test execution
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_k8s: marks tests that require Kubernetes access"
    )
    config.addinivalue_line(
        "markers", "requires_terraform: marks tests that require Terraform"
    )


# Skip tests based on environment
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on available resources."""
    import subprocess
    
    # Check Terraform availability
    try:
        subprocess.run(["terraform", "--version"], capture_output=True, timeout=5)
        terraform_available = True
    except:
        terraform_available = False
    
    # Check kubectl availability
    try:
        subprocess.run(["kubectl", "version", "--client"], capture_output=True, timeout=5)
        kubectl_available = True
    except:
        kubectl_available = False
    
    skip_terraform = pytest.mark.skip(reason="Terraform not available")
    skip_k8s = pytest.mark.skip(reason="kubectl not available")
    
    for item in items:
        if "requires_terraform" in item.keywords and not terraform_available:
            item.add_marker(skip_terraform)
        if "requires_k8s" in item.keywords and not kubectl_available:
            item.add_marker(skip_k8s)
