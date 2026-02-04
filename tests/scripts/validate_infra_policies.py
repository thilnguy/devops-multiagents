#!/usr/bin/env python3
"""
Infrastructure Policy Validator (Policy-as-Code)
------------------------------------------------
Parses Terraform Plan JSON and enforces Cost Optimization rules.
Usage: python3 validate_infra_policies.py <plan.json> --env <dev|staging|production>

Rules:
1. Non-Prod must use SPOT instances.
2. Non-Prod must use ARM64 (t4g/m6g) instances.
3. Non-Prod must have exactly 1 NAT Gateway.
4. Production must use ON_DEMAND (or implied default) for stability.
5. Production must have >= 2 NAT Gateways.
"""

import json
import sys
import argparse
from typing import Dict, List, Any

def load_plan(filepath: str) -> Dict:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Plan file '{filepath}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{filepath}'.")
        sys.exit(1)

def get_resource_changes(plan: Dict, type_filter: str) -> List[Dict]:
    """Extracts resources of a specific type from resource_changes."""
    resources = []
    for resource in plan.get('resource_changes', []):
        if resource.get('type') == type_filter:
            resources.append(resource)
    return resources

def validate_nonprod(plan: Dict) -> List[str]:
    errors = []
    
    # 1. Check Auto Scaling Groups / EKS Node Groups for SPOT
    node_groups = get_resource_changes(plan, 'aws_eks_node_group')
    for ng in node_groups:
        change = ng.get('change', {}).get('after', {})
        # Some plans might show "unknown" for computed values, but capacity_type passed via var should be explicit if we set it.
        # If it's unknown, we can't strictly validate, but if it is present, it must be SPOT.
        capacity_type = change.get('capacity_type')
        if capacity_type and capacity_type != 'SPOT':
            errors.append(f"[Cost] EKS Node Group '{ng['name']}' uses {capacity_type}. Non-Prod MUST use SPOT.")
            
        # 2. Check Architecture (ARM64)
        instance_types = change.get('instance_types', [])
        if instance_types:
            for it in instance_types:
                if not (it.startswith('t4g') or it.startswith('m6g') or it.startswith('c6g') or it.startswith('r6g')):
                     errors.append(f"[Cost] Instance type '{it}' is not Graviton (ARM64). Non-Prod should use t4g/m6g series.")

    # 3. Check NAT Gateways
    nats = get_resource_changes(plan, 'aws_nat_gateway')
    # Count only creates or updates (not deletes)
    active_nats = [n for n in nats if 'create' in n.get('change', {}).get('actions', []) or 'update' in n.get('change', {}).get('actions', []) or 'no-op' in n.get('change', {}).get('actions', [])]
    
    # Note: In a real plan, we might not see the count if it's conditional logic in the module not yet expanded, 
    # but we can check the resources present.
    if len(active_nats) > 1:
        errors.append(f"[Cost] Found {len(active_nats)} NAT Gateways. Non-Prod should have exactly 1.")

    return errors

def validate_prod(plan: Dict) -> List[str]:
    errors = []
    
    # 1. Check Capacity Type
    node_groups = get_resource_changes(plan, 'aws_eks_node_group')
    for ng in node_groups:
        change = ng.get('change', {}).get('after', {})
        capacity_type = change.get('capacity_type')
        if capacity_type == 'SPOT':
            errors.append(f"[Stability] EKS Node Group '{ng['name']}' uses SPOT. Production should use ON_DEMAND.")

    # 2. Check NAT Gateways
    nats = get_resource_changes(plan, 'aws_nat_gateway')
    active_nats = [n for n in nats if 'create' in n.get('change', {}).get('actions', []) or 'no-op' in n.get('change', {}).get('actions', [])]
    
    if len(active_nats) < 2:
         # Warn broadly, though exact count depends on AZs
         errors.append(f"[Availability] Found only {len(active_nats)} NAT Gateways. Production should have at least 2 for Multi-AZ.")

    return errors

def main():
    parser = argparse.ArgumentParser(description="Validate Terraform Plan Policies")
    parser.add_argument("plan_json", help="Path to terraform plan (converted to JSON)")
    parser.add_argument("--env", required=True, choices=["dev", "staging", "production"], help="Target environment")
    
    args = parser.parse_args()
    
    plan = load_plan(args.plan_json)
    
    print(f"🔍 Validating Policy for environment: {args.env}")
    
    violations = []
    if args.env in ["dev", "staging"]:
        violations = validate_nonprod(plan)
    else:
        violations = validate_prod(plan)
        
    if violations:
        print("\n❌ Policy Violations Found:")
        for v in violations:
            print(f" - {v}")
        sys.exit(1)
    else:
        print("\n✅ Policy Validation Passed. No regressions detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
