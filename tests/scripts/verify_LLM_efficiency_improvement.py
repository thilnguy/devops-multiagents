#!/usr/bin/env python3
"""
Deep Verification Suite for LLM Efficiency Tools
Tests correctness, edge cases, and logic for:
1. analyze_logs.py
2. summarize_infra.py
3. archive_memory.py & search_memory.py
"""

import unittest
import os
import json
import shutil
import tempfile
import sys
from io import StringIO
from contextlib import redirect_stdout

# Import the modules to test. We need to add the project root to path.
PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJ_ROOT)

# Run from a clean environment by copying scripts to a temp location or just invoking them?
# Better to import them if possible, but they are scripts. 
# We'll use subprocess or import if they are structured as modules.
# They are scripts with `if __name__ == "__main__"`, so we can import functions.

# Importing using full path logic or sys.path
sys.path.append(os.path.join(PROJ_ROOT, "scripts"))

try:
    import analyze_logs
    import summarize_infra
    import archive_memory
    import search_memory
except ImportError as e:
    print(f"Failed to import scripts: {e}")
    sys.exit(1)

class TestAnalyzeLogs(unittest.TestCase):
    def test_variable_tokenization(self):
        """Test that timestamps, IPs, and numbers are correctly tokenized."""
        # Use a long number to ensure it triggers the <NUM> replacement (>= 5 digits)
        line = "2024-05-20 10:00:01 [ERROR] IP 192.168.1.5 failed connection attempt 123456"
        tokenized = analyze_logs.tokenize_line(line)
        # We expect <TIMESTAMP> to be present, and the long number to be <NUM>
        expected = "<TIMESTAMP> [ERROR] IP <IP> failed connection attempt <NUM>"
        self.assertEqual(tokenized, expected)

    def test_clustering_logic(self):
        """Test that similar lines cluster together."""
        # Use long numbers so they are treated as variables and clustered
        lines = [
            "Error at process 100001",
            "Error at process 100002",
            "Error at process 100003"
        ]
        # We need to simulate the file reading or cluster logic directly if exposed.
        # Since analyze_logs reads a file, we'll write a temp file.
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp.write("\n".join(lines))
            tmp_path = tmp.name
        
        try:
            # Capture stdout
            f = StringIO()
            with redirect_stdout(f):
                analyze_logs.analyze_logs(tmp_path)
            output = f.getvalue()
            
            # The tool prints the SAMPLE line, not the tokenized pattern.
            # So we expect to see one of the original lines, but with [3x] count.
            self.assertIn("[3x] Error at process 100001", output)
        finally:
            os.remove(tmp_path)

    def test_noise_filtering(self):
        """Test that INFO/DEBUG are filtered by default."""
        lines = [
            "[INFO] System started",
            "[DEBUG] Variable x=5",
            "[ERROR] Critical failure"
        ]
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp.write("\n".join(lines))
            tmp_path = tmp.name
        
        try:
            f = StringIO()
            with redirect_stdout(f):
                analyze_logs.analyze_logs(tmp_path, show_info=False)
            output = f.getvalue()
            
            self.assertNotIn("[INFO]", output)
            self.assertNotIn("[DEBUG]", output)
            self.assertIn("[ERROR]", output)
            
            # Test with show_info=True
            f = StringIO()
            with redirect_stdout(f):
                analyze_logs.analyze_logs(tmp_path, show_info=True)
            output = f.getvalue()
            self.assertIn("[INFO]", output)
        finally:
            os.remove(tmp_path)


class TestSummarizeInfra(unittest.TestCase):
    def test_simplify_resource_aws_instance(self):
        """Test simplification of AWS Instance resource."""
        resource = {
            "type": "aws_instance",
            "name": "web",
            "values": {
                "id": "i-123456",
                "instance_type": "t3.micro",
                "public_ip": "1.2.3.4",
                "private_ip": "10.0.0.1",
                "other_field": "ignored"
            }
        }
        summary = summarize_infra.simplify_resource(resource)
        self.assertEqual(summary['id'], "i-123456")
        self.assertEqual(summary['instance_type'], "t3.micro")
        self.assertNotIn('other_field', summary)

    def test_traverse_module_structure(self):
        """Test traversal of nested modules."""
        mock_data = {
            "values": {
                "root_module": {
                    "resources": [{"type": "r1", "name": "n1", "mode": "managed", "values": {"id": "1"}}],
                    "child_modules": [
                        {
                            "resources": [{"type": "r2", "name": "n2", "mode": "managed", "values": {"id": "2"}}]
                        }
                    ]
                }
            }
        }
        
        # We need to mock get_terraform_output or create a state file.
        # Let's mock the `get_terraform_output` function for this test context.
        original_func = summarize_infra.get_terraform_output
        summarize_infra.get_terraform_output = lambda x: mock_data
        
        f = StringIO()
        with redirect_stdout(f):
            summarize_infra.summarize_state("dummy_path")
        
        output_json = json.loads(f.getvalue())
        summarize_infra.get_terraform_output = original_func # Restore
        
        self.assertEqual(output_json['resource_count'], 2)
        names = [r['name'] for r in output_json['resources']]
        self.assertIn('n1', names)
        self.assertIn('n2', names)


class TestMemoryRAG(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Patch the paths in the modules to use temp dir
        self.original_active = archive_memory.ACTIVE_FILE
        self.original_archive = archive_memory.ARCHIVE_FILE
        self.original_search_active = search_memory.ACTIVE_FILE
        self.original_search_archive = search_memory.ARCHIVE_FILE
        
        self.active_path = os.path.join(self.test_dir, "memory.json")
        self.archive_path = os.path.join(self.test_dir, "archived_memory.json")
        
        archive_memory.ACTIVE_FILE = self.active_path
        archive_memory.ARCHIVE_FILE = self.archive_path
        search_memory.ACTIVE_FILE = self.active_path
        search_memory.ARCHIVE_FILE = self.archive_path
        
        archive_memory.MAX_ACTIVE_LEARNINGS = 2 # Set low for testing

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        # Restore paths
        archive_memory.ACTIVE_FILE = self.original_active
        archive_memory.ARCHIVE_FILE = self.original_archive
        search_memory.ACTIVE_FILE = self.original_search_active
        search_memory.ARCHIVE_FILE = self.original_search_archive

    def test_archive_logic(self):
        """Test that learnings exceeding limit are archived."""
        # Create active memory with 5 items (Limit is 2)
        learnings = [{'id': f'L{i}', 'pattern': f'P{i}'} for i in range(1, 6)]
        data = {'learnings': learnings}
        
        with open(self.active_path, 'w') as f:
            json.dump(data, f)
            
        # Run archive
        f = StringIO()
        with redirect_stdout(f):
            archive_memory.archive_memory()
            
        # Verify Active has 2 items (L4, L5)
        with open(self.active_path, 'r') as f:
            active = json.load(f)
        self.assertEqual(len(active['learnings']), 2)
        self.assertEqual(active['learnings'][0]['id'], 'L4')
        
        # Verify Archive has 3 items (L1, L2, L3)
        with open(self.archive_path, 'r') as f:
            archived = json.load(f)
        self.assertEqual(len(archived['learnings']), 3)
        self.assertEqual(archived['learnings'][0]['id'], 'L1')

    def test_search_relevance(self):
        """Test search finds relevant items in both active and archive."""
        # Setup data
        active_items = [{'id': 'A1', 'pattern': 'Terraform lock error', 'resolution': 'Force unlock'}]
        archive_items = [{'id': 'B1', 'pattern': 'Kubernetes pod crash', 'resolution': 'Check logs'}]
        
        with open(self.active_path, 'w') as f:
            json.dump({'learnings': active_items}, f)
        with open(self.archive_path, 'w') as f:
            json.dump({'learnings': archive_items}, f)
            
        # 1. Search for "Terraform" (Active)
        f = StringIO()
        with redirect_stdout(f):
            search_memory.search_memory("Terraform")
        output = f.getvalue()
        self.assertIn("A1", output)
        self.assertNotIn("B1", output)
        
        # 2. Search for "pod" (Archive)
        f = StringIO()
        with redirect_stdout(f):
            search_memory.search_memory("pod")
        output = f.getvalue()
        self.assertIn("B1", output)
        self.assertNotIn("A1", output)

if __name__ == '__main__':
    print("Running Deep Verification Suite for LLM efficiency improvement...")
    unittest.main(verbosity=2)
