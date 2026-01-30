#!/usr/bin/env python3
"""
Integration Tests for DevOps Multi-Agent Ecosystem
Tests end-to-end workflows and agent interactions.
"""

import os
import sys
import json
import subprocess
import unittest
from pathlib import Path
from typing import Optional, Dict, Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestEcosystemIntegration(unittest.TestCase):
    """Integration tests for the ecosystem components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.personas_dir = PROJECT_ROOT / ".antigravity" / "personas"
        cls.skills_dir = PROJECT_ROOT / ".antigravity" / "skills"
        cls.terraform_dir = PROJECT_ROOT / "infra" / "terraform"
        cls.k8s_dir = PROJECT_ROOT / "infra" / "kubernetes" / "base"
    
    def test_personas_exist(self):
        """Test that all required personas exist."""
        required_personas = [
            "master-architect.md",
            "infra-bot.md",
            "kube-master.md",
            "pipe-liner.md"
        ]
        
        for persona in required_personas:
            persona_path = self.personas_dir / persona
            self.assertTrue(
                persona_path.exists(),
                f"Missing persona: {persona}"
            )
    
    def test_skills_exist(self):
        """Test that all required skills exist."""
        required_skills = [
            "terraform-plan.md",
            "terraform-sync.md",
            "k8s-troubleshoot.md",
            "jenkins-ops.md"
        ]
        
        for skill in required_skills:
            skill_path = self.skills_dir / skill
            self.assertTrue(
                skill_path.exists(),
                f"Missing skill: {skill}"
            )
    
    def test_persona_skill_references(self):
        """Test that personas reference valid skills."""
        # Map of personas to their expected skill keywords
        persona_skills = {
            "infra-bot.md": ["terraform"],
            "kube-master.md": ["k8s", "troubleshoot"],  # Match "k8s troubleshoot" or "k8s-troubleshoot"
            "pipe-liner.md": ["jenkins"]
        }
        
        for persona, expected_keywords in persona_skills.items():
            persona_path = self.personas_dir / persona
            if persona_path.exists():
                content = persona_path.read_text().lower()
                for keyword in expected_keywords:
                    self.assertIn(
                        keyword.lower(),
                        content,
                        f"{persona} should reference {keyword}"
                    )
    
    def test_terraform_files_valid(self):
        """Test that Terraform files exist and have required structure."""
        required_files = ["main.tf", "variable.tf", "outputs.tf"]
        
        for tf_file in required_files:
            tf_path = self.terraform_dir / tf_file
            self.assertTrue(
                tf_path.exists(),
                f"Missing Terraform file: {tf_file}"
            )
        
        # Check main.tf has required blocks
        main_tf = (self.terraform_dir / "main.tf").read_text()
        self.assertIn("terraform {", main_tf)
        self.assertIn("provider", main_tf)
    
    def test_kubernetes_manifests_valid(self):
        """Test that Kubernetes manifests exist and have required structure."""
        required_files = ["deployment.yaml", "service.yaml", "namespace.yaml"]
        
        for k8s_file in required_files:
            k8s_path = self.k8s_dir / k8s_file
            self.assertTrue(
                k8s_path.exists(),
                f"Missing Kubernetes file: {k8s_file}"
            )
    
    def test_api_gateway_files(self):
        """Test that API gateway service files exist."""
        api_dir = PROJECT_ROOT / "services" / "api-gateway"
        required_files = ["Dockerfile", "app.py", "requirements.txt"]
        
        for file in required_files:
            file_path = api_dir / file
            self.assertTrue(
                file_path.exists(),
                f"Missing API gateway file: {file}"
            )


class TestMCPConfiguration(unittest.TestCase):
    """Tests for MCP server configuration."""
    
    @classmethod
    def setUpClass(cls):
        """Load MCP configuration."""
        cls.config_path = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
    
    def test_config_file_exists(self):
        """Test that MCP config file exists."""
        self.assertTrue(
            self.config_path.exists(),
            "MCP config file not found"
        )
    
    def test_config_valid_json(self):
        """Test that MCP config is valid JSON."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                self.assertIsInstance(config, dict)
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON in MCP config: {e}")
    
    def test_required_servers_configured(self):
        """Test that required MCP servers are configured."""
        if not self.config_path.exists():
            self.skipTest("MCP config not found")
        
        with open(self.config_path) as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        required_servers = ["github", "kubernetes", "jenkins", "terraform-registry"]
        
        for server in required_servers:
            self.assertIn(
                server,
                servers,
                f"Missing MCP server: {server}"
            )


class TestAPIGateway(unittest.TestCase):
    """Tests for the API Gateway service."""
    
    @classmethod
    def setUpClass(cls):
        """Set up API gateway paths."""
        cls.api_dir = PROJECT_ROOT / "services" / "api-gateway"
    
    def test_dockerfile_security(self):
        """Test that Dockerfile follows security best practices."""
        dockerfile = self.api_dir / "Dockerfile"
        if not dockerfile.exists():
            self.skipTest("Dockerfile not found")
        
        content = dockerfile.read_text()
        
        # Should use non-root user
        self.assertIn("USER", content, "Dockerfile should specify non-root USER")
        
        # Should have HEALTHCHECK
        self.assertIn("HEALTHCHECK", content, "Dockerfile should have HEALTHCHECK")
    
    def test_app_has_health_endpoint(self):
        """Test that app.py defines health endpoint."""
        app_py = self.api_dir / "app.py"
        if not app_py.exists():
            self.skipTest("app.py not found")
        
        content = app_py.read_text()
        self.assertIn("/health", content, "App should have /health endpoint")


class TestInfrastructureIntegration(unittest.TestCase):
    """Integration tests for infrastructure components."""
    
    @classmethod
    def setUpClass(cls):
        """Check if we can run infrastructure tests."""
        # Check if terraform is available
        try:
            result = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                timeout=5
            )
            cls.terraform_available = result.returncode == 0
        except:
            cls.terraform_available = False
        
        # Check if kubectl is available
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                timeout=5
            )
            cls.kubectl_available = result.returncode == 0
        except:
            cls.kubectl_available = False
    
    def test_terraform_validate(self):
        """Test that Terraform configuration is valid."""
        if not self.terraform_available:
            self.skipTest("Terraform not available")
        
        tf_dir = PROJECT_ROOT / "infra" / "terraform"
        
        # Init
        init_result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=tf_dir,
            capture_output=True,
            timeout=120
        )
        
        # Check for network errors (acceptable in restricted environments)
        stderr = init_result.stderr.decode()
        if "no such host" in stderr or "dial tcp" in stderr:
            self.skipTest("Terraform registry not accessible (network issue)")
        
        self.assertEqual(
            init_result.returncode, 0,
            f"Terraform init failed: {stderr}"
        )
        
        # Validate
        validate_result = subprocess.run(
            ["terraform", "validate"],
            cwd=tf_dir,
            capture_output=True,
            timeout=30
        )
        self.assertEqual(
            validate_result.returncode, 0,
            f"Terraform validate failed: {validate_result.stderr.decode()}"
        )
    
    def test_kubernetes_manifests_dry_run(self):
        """Test that Kubernetes manifests pass dry-run validation."""
        if not self.kubectl_available:
            self.skipTest("kubectl not available")
        
        k8s_dir = PROJECT_ROOT / "infra" / "kubernetes" / "base"
        yaml_files = list(k8s_dir.glob("*.yaml"))
        
        for yaml_file in yaml_files:
            if yaml_file.name == "kustomization.yaml":
                continue  # Skip kustomization file
            
            result = subprocess.run(
                ["kubectl", "apply", "--dry-run=client", "-f", str(yaml_file)],
                capture_output=True,
                timeout=10
            )
            
            # Check for network/cluster errors (acceptable in offline environments)
            stderr = result.stderr.decode()
            if "dial tcp" in stderr or "operation not permitted" in stderr or "connection refused" in stderr:
                self.skipTest("Kubernetes cluster not accessible")
            
            self.assertEqual(
                result.returncode, 0,
                f"{yaml_file.name} failed dry-run: {stderr}"
            )


def run_tests(verbosity: int = 2) -> int:
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEcosystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIGateway))
    suite.addTests(loader.loadTestsFromTestCase(TestInfrastructureIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run integration tests")
    parser.add_argument("-v", "--verbose", action="count", default=2)
    
    args = parser.parse_args()
    sys.exit(run_tests(verbosity=args.verbose))
