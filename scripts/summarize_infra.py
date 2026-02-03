#!/usr/bin/env python3
"""
Terraform State Summarizer
Parses terraform.tfstate or uses `terraform show -json` to produce a 
lightweight resource graph for LLM context.
"""

import json
import sys
import subprocess
import os

def get_terraform_output(tf_dir):
    """Run terraform show -json to get state."""
    if not os.path.exists(os.path.join(tf_dir, ".terraform")):
        print("Note: .terraform directory not found. Assuming offline or uninitialized.")
        # Fallback to reading state file directly if it exists
        state_path = os.path.join(tf_dir, "terraform.tfstate")
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                return json.load(f)
        return None

    try:
        result = subprocess.run(
            ["terraform", "show", "-json"],
            cwd=tf_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running terraform show: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print("Error analyzing terraform output.")
        return None

def simplify_resource(resource):
    """Extract key fields from a resource."""
    # Common useful attributes across most AWS/K8s resources
    attributes = resource.get('values', {})
    
    summary = {
        "address": resource.get('address'),
        "type": resource.get('type'),
        "name": resource.get('name'),
        "id": attributes.get('id', 'N/A')
    }

    # Resource specific interesting fields
    if resource.get('type') == 'aws_vpc':
        summary['cidr_block'] = attributes.get('cidr_block')
    
    elif resource.get('type') == 'aws_instance':
        summary['instance_type'] = attributes.get('instance_type')
        summary['public_ip'] = attributes.get('public_ip')
        summary['private_ip'] = attributes.get('private_ip')
    
    elif resource.get('type') == 'aws_eks_cluster':
        summary['version'] = attributes.get('version')
        summary['status'] = attributes.get('status')
    
    elif resource.get('type') == 'kubernetes_service':
        spec = attributes.get('spec', [{}])[0]
        summary['cluster_ip'] = spec.get('cluster_ip')
        summary['ports'] = spec.get('port')
    
    return summary

def traverse_modules(module, resources_list):
    """Recursively traverse modules to find resources."""
    # Direct resources
    if 'resources' in module:
        for res in module['resources']:
            # We only care about managed resources, not data sources often
            if res.get('mode') == 'managed':
                resources_list.append(simplify_resource(res))

    # Child modules
    if 'child_modules' in module:
        for child in module['child_modules']:
            traverse_modules(child, resources_list)

def summarize_state(tf_dir):
    data = get_terraform_output(tf_dir)
    
    if not data:
        print(json.dumps({"error": "No state found or terraform error", "resources": []}, indent=2))
        return

    # Terraform JSON output structure
    # root_module (values) -> child_modules ...
    
    resources = []
    
    # Should handle both direct state file structure and `terraform show -json` output
    # `terraform show -json` usually wraps in "values" -> "root_module"
    
    root = data.get('values', {}).get('root_module', {})
    if not root and 'resources' in data: 
        # Raw v4 state file format
        raw_resources = data.get('resources', [])
        for res in raw_resources:
             # Basic mapping for raw state file which has flattened resources
             summary = {
                 "address": f"{res.get('type')}.{res.get('name')}",
                 "type": res.get('type'),
                 "name": res.get('name'),
             }
             # Attributes are nested in instances
             if res.get('instances'):
                 summary['id'] = res['instances'][0].get('attributes', {}).get('id')
             resources.append(summary)
    else:
        traverse_modules(root, resources)

    output = {
        "summary": "Terraform Infrastructure Graph",
        "resource_count": len(resources),
        "resources": resources
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./summarize_infra.py <path_to_terraform_dir>")
        sys.exit(1)
        
    tf_dir = sys.argv[1]
    summarize_state(tf_dir)
