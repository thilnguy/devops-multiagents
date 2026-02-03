#!/usr/bin/env python3
"""
Ecosystem Validation Script
Checks logical consistency between Personas, Skills, and MCP Servers.
"""

import os
import re
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAS_DIR = os.path.join(PROJECT_ROOT, ".antigravity", "personas")
SKILLS_DIR = os.path.join(PROJECT_ROOT, ".antigravity", "skills")
MCP_CONFIG_PATH = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")

def load_mcp_servers():
    """Load MCP server names from config."""
    if os.path.exists(MCP_CONFIG_PATH):
        with open(MCP_CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return list(config.get("mcpServers", {}).keys())
    return []

def parse_frontmatter(filepath):
    """Parse YAML frontmatter from a markdown file using simple regex."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    frontmatter = {}
    body = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            # Simple key: value parsing
            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    
    return frontmatter, body


def extract_skill_references(content):
    """Extract skill references from persona content."""
    # Look for patterns like: `skill-name`, skill-name.md, or Skills: section
    skills = []
    # Pattern for markdown links to skills
    link_pattern = r'\[([^\]]+)\]\([^)]*skills/([^)]+)\.md\)'
    for match in re.finditer(link_pattern, content):
        skills.append(match.group(2))
    
    # Pattern for backtick references
    backtick_pattern = r'`([a-z0-9-]+(?:-[a-z0-9]+)*)`'
    for match in re.finditer(backtick_pattern, content):
        potential_skill = match.group(1)
        if os.path.exists(os.path.join(SKILLS_DIR, f"{potential_skill}.md")):
            skills.append(potential_skill)
    
    return list(set(skills))

def extract_mcp_references(content):
    """Extract MCP server references from skill content."""
    servers = []
    # Look for various patterns
    patterns = [
        r'`mcp_([a-z-]+)_',  # Tool calls like mcp_kubernetes_pods_list
        r'`([a-z-]+)-mcp-server`',  # Package names
        r'MCP Server[:\s]*\n-\s*`([^`]+)`',  # Required MCP Server section
        r'`([a-z-]+)`\s*\(provides',  # Server name followed by (provides...)
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            servers.append(match.group(1).lower().replace('_', '-'))
    
    return list(set(servers))

def normalize_mcp_name(name):
    """Normalize MCP server name for comparison."""
    return name.lower().replace('-', '').replace('_', '')

def mcp_names_match(ref, server):
    """Check if a reference matches a configured server."""
    ref_norm = normalize_mcp_name(ref)
    srv_norm = normalize_mcp_name(server)
    return ref_norm == srv_norm or ref_norm in srv_norm or srv_norm in ref_norm


def validate_personas():
    """Validate all persona files."""
    print("=" * 60)
    print("PERSONA VALIDATION")
    print("=" * 60)
    issues = []
    
    for filename in os.listdir(PERSONAS_DIR):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(PERSONAS_DIR, filename)
        frontmatter, content = parse_frontmatter(filepath)
        
        print(f"\n📋 {filename}")
        
        # Check frontmatter
        if not frontmatter:
            issues.append(f"{filename}: Missing YAML frontmatter")
            print("   ❌ Missing YAML frontmatter")
        else:
            if 'name' not in frontmatter:
                issues.append(f"{filename}: Missing 'name' in frontmatter")
                print("   ⚠️ Missing 'name' in frontmatter")
            else:
                print(f"   ✅ Name: {frontmatter['name']}")
            
            if 'description' not in frontmatter:
                issues.append(f"{filename}: Missing 'description' in frontmatter")
                print("   ⚠️ Missing 'description' in frontmatter")
        
        # Check content is not empty
        if len(content.strip()) < 50:
            issues.append(f"{filename}: Content too short (< 50 chars)")
            print("   ❌ Content too short")
        else:
            print(f"   ✅ Content length: {len(content)} chars")
        
        # Extract skill references
        skills = extract_skill_references(content)
        if skills:
            print(f"   📎 Referenced skills: {', '.join(skills)}")
    
    return issues

def validate_skills():
    """Validate all skill files."""
    print("\n" + "=" * 60)
    print("SKILL VALIDATION")
    print("=" * 60)
    issues = []
    mcp_servers = load_mcp_servers()
    
    for filename in os.listdir(SKILLS_DIR):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(SKILLS_DIR, filename)
        frontmatter, content = parse_frontmatter(filepath)
        
        print(f"\n🔧 {filename}")
        
        # Check frontmatter
        if not frontmatter:
            issues.append(f"{filename}: Missing YAML frontmatter")
            print("   ❌ Missing YAML frontmatter")
        else:
            if 'name' not in frontmatter:
                issues.append(f"{filename}: Missing 'name' in frontmatter")
            else:
                print(f"   ✅ Name: {frontmatter['name']}")
        
        # Check content is not empty
        if len(content.strip()) < 50:
            issues.append(f"{filename}: Content too short (< 50 chars)")
            print("   ❌ Content too short or EMPTY")
        else:
            print(f"   ✅ Content length: {len(content)} chars")
        
        # Extract MCP references and validate
        mcp_refs = extract_mcp_references(content)
        if mcp_refs:
            print(f"   🔌 MCP references: {', '.join(mcp_refs)}")
            for ref in mcp_refs:
                # Use improved matching
                matched = any(mcp_names_match(ref, srv) for srv in mcp_servers)
                if not matched:
                    issues.append(f"{filename}: References unknown MCP server '{ref}'")
                    print(f"      ⚠️ '{ref}' not found in mcp_config.json")

    
    return issues

def validate_mcp_config():
    """Validate MCP configuration."""
    print("\n" + "=" * 60)
    print("MCP CONFIG VALIDATION")
    print("=" * 60)
    issues = []
    
    if not os.path.exists(MCP_CONFIG_PATH):
        issues.append("mcp_config.json not found")
        print("❌ mcp_config.json not found")
        return issues
    
    servers = load_mcp_servers()
    print(f"✅ Found {len(servers)} MCP servers: {', '.join(servers)}")
    
    # Check for placeholder credentials
    with open(MCP_CONFIG_PATH, 'r') as f:
        content = f.read()
        if 'your-' in content.lower() or 'placeholder' in content.lower():
            issues.append("mcp_config.json contains placeholder credentials")
            print("⚠️ Contains placeholder credentials that need to be filled")
    
    return issues

def main():
    print("\n🔍 DEVOPS ECOSYSTEM VALIDATION\n")
    
    all_issues = []
    all_issues.extend(validate_personas())
    all_issues.extend(validate_skills())
    all_issues.extend(validate_mcp_config())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all_issues:
        print(f"\n⚠️ Found {len(all_issues)} issue(s):\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        return 1
    else:
        print("\n✅ All validations passed! Ecosystem is consistent.")
        return 0

if __name__ == "__main__":
    exit(main())
