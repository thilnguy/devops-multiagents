import os
import json
import subprocess

def check_mcp_config():
    """Verify system MCP configuration file"""
    # Config path from user's environment
    config_path = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")
    
    print("🔍 [1/3] Checking MCP configuration file...")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                servers = config.get("mcpServers", {})
                print(f"✅ Found {len(servers)} servers: {', '.join(servers.keys())}")
                
                # Specifically check 'mcp-fetch' and 'jenkins' servers
                if "mcp-fetch" in servers:
                    print("   ✨ Server 'mcp-fetch' is configured.")
                if "jenkins" in servers:
                    print("   ✨ Server 'jenkins' is configured.")
                else:
                    print("   ⚠️ Server 'jenkins' is missing from config.")
                return servers
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return None
    else:
        print(f"❌ File not found at: {config_path}")
        return None

def check_project_structure():
    """Verify if Personas and Skills are defined"""
    print("\n🔍 [2/3] Checking .antigravity/ Project structure...")
    required_dirs = [".antigravity/personas", ".antigravity/skills"]
    cwd = os.getcwd()
    
    for d in required_dirs:
        dir_path = os.path.join(cwd, d)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"✅ {d}: {len(files)} files ready.")
            
            # Check for mcp-fetch-docs skill
            if d == ".antigravity/skills":
                if "mcp-fetch-docs.md" in files:
                    print("   ✨ Skill 'mcp-fetch-docs' exists.")
                else:
                    print("   ⚠️ Missing skill 'mcp-fetch-docs.md'.")
        else:
            print(f"⚠️ Missing directory: {d}")

def check_cli_tools():
    """Check command line tools that MCP depends on"""
    print("\n🔍 [3/4] Checking CLI Tools (Dependencies)...")
    # Each tool may have a different way to check version
    tools = {
        "gh": ["--version"],
        "terraform": ["--version"],
        "npx": ["--version"],
        "kubectl": ["version", "--client"]
    }
    for tool, args in tools.items():
        try:
            subprocess.run([tool] + args, capture_output=True, check=True)
            print(f"✅ {tool.upper()} is installed.")
        except FileNotFoundError:
            print(f"❌ {tool.upper()} is not installed (Command not found in PATH).")
        except subprocess.CalledProcessError:
            # Some tools might return non-zero exit code but still exist
            print(f"⚠️ {tool.upper()} is installed but returned a warning during version check.")
        except Exception as e:
            print(f"❌ Error checking {tool.upper()}: {e}")

def validate_mcp_servers(servers):
    """Check if MCP servers are executable"""
    print("\n🔍 [4/4] Checking MCP Servers readiness...")
    if not servers:
        print("⚠️ No servers to check.")
        return

    for name, config in servers.items():
        command = config.get("command")
        args = config.get("args", [])
        
        print(f"   ⚙️ Checking server '{name}'...")
        
        # Check if it's an npx command
        if command and ("npx" in command):
            # Find package name in args (first element not starting with '-')
            package = next((arg for arg in args if not arg.startswith("-")), None)
            if package:
                try:
                    # Run 'npm view' to check if package exists (faster than info)
                    result = subprocess.run(["npm", "view", package, "name"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"      ✅ Package '{package}' exists on npm registry.")
                    else:
                        error_msg = result.stderr.strip()
                        if "404" in error_msg:
                            print(f"      ❌ Package '{package}' DOES NOT EXIST on npm. Please check the package name.")
                        elif "Access token expired" in error_msg:
                            print(f"      ⚠️ npm auth error (Access token expired), but package might still exist.")
                        else:
                            print(f"      ❌ Error checking package '{package}': {error_msg.splitlines()[0] if error_msg else 'Unknown error'}")
                except subprocess.TimeoutExpired:
                    print(f"      ⚠️ Timeout checking package '{package}'.")
                except Exception as e:
                    print(f"      ❌ Error checking package '{package}': {e}")
            else:
                print(f"      ⚠️ Package name not found in args for '{name}'.")
        else:
            # Check if command exists
            try:
                # Use which to check command
                subprocess.run(["which", command], capture_output=True, check=True)
                print(f"      ✅ Command '{command}' found in system.")
            except subprocess.CalledProcessError:
                print(f"      ❌ Command '{command}' not found in PATH.")
            except Exception as e:
                print(f"      ⚠️ Unable to verify command '{command}': {e}")

if __name__ == "__main__":
    print("=== ANTIGRAVITY DEVOPS ECOSYSTEM HEALTH CHECK ===\n")
    servers = check_mcp_config()
    check_project_structure()
    check_cli_tools()
    validate_mcp_servers(servers)
    print("\n🚀 Health check complete!")