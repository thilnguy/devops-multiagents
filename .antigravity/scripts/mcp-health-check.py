import os
import json
import subprocess

def check_mcp_config():
    """Kiểm tra file cấu hình MCP của hệ thống"""
    # Đường dẫn config từ request của user
    config_path = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")
    
    print("🔍 [1/3] Kiểm tra file cấu hình MCP...")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                servers = config.get("mcpServers", {})
                print(f"✅ Tìm thấy {len(servers)} servers: {', '.join(servers.keys())}")
                
                # Kiểm tra riêng server 'mcp-fetch' và 'jenkins'
                if "mcp-fetch" in servers:
                    print("   ✨ Server 'mcp-fetch' đã được cấu hình.")
                if "jenkins" in servers:
                    print("   ✨ Server 'jenkins' đã được cấu hình.")
                else:
                    print("   ⚠️ Server 'jenkins' chưa xuất hiện trong config.")
                return servers
        except Exception as e:
            print(f"❌ Lỗi khi đọc file config: {e}")
            return None
    else:
        print(f"❌ Không tìm thấy file tại: {config_path}")
        return None

def check_project_structure():
    """Kiểm tra các Persona và Skill đã được định nghĩa chưa"""
    print("\n🔍 [2/3] Kiểm tra cấu trúc Project .antigravity/...")
    required_dirs = [".antigravity/personas", ".antigravity/skills"]
    cwd = os.getcwd()
    
    for d in required_dirs:
        dir_path = os.path.join(cwd, d)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"✅ {d}: {len(files)} files sẵn sàng.")
            
            # Kiểm tra skill mcp-fetch-docs
            if d == ".antigravity/skills":
                if "mcp-fetch-docs.md" in files:
                    print("   ✨ Skill 'mcp-fetch-docs' đã tồn tại.")
                else:
                    print("   ⚠️ Thiếu skill 'mcp-fetch-docs.md'.")
        else:
            print(f"⚠️ Thiếu thư mục: {d}")

def check_cli_tools():
    """Kiểm tra các công cụ dòng lệnh mà MCP phụ thuộc vào"""
    print("\n🔍 [3/4] Kiểm tra CLI Tools (Dependencies)...")
    # Mỗi công cụ có thể có cách kiểm tra version khác nhau
    tools = {
        "gh": ["--version"],
        "terraform": ["--version"],
        "npx": ["--version"],
        "kubectl": ["version", "--client"]
    }
    for tool, args in tools.items():
        try:
            subprocess.run([tool] + args, capture_output=True, check=True)
            print(f"✅ {tool.upper()} đã được cài đặt.")
        except FileNotFoundError:
            print(f"❌ {tool.upper()} chưa được cài đặt (Không tìm thấy lệnh trong PATH).")
        except subprocess.CalledProcessError:
            # Một số tool có thể trả về exit code khác 0 nhưng vẫn tồn tại
            print(f"⚠️ {tool.upper()} đã được cài đặt nhưng có cảnh báo khi kiểm tra version.")
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra {tool.upper()}: {e}")

def validate_mcp_servers(servers):
    """Kiểm tra xem các server MCP có thể chạy được không"""
    print("\n🔍 [4/4] Kiểm tra tính sẵn sàng của MCP Servers...")
    if not servers:
        print("⚠️ Không có server nào để kiểm tra.")
        return

    for name, config in servers.items():
        command = config.get("command")
        args = config.get("args", [])
        
        print(f"   ⚙️ Đang kiểm tra server '{name}'...")
        
        # Kiểm tra nếu là npx command
        if command and ("npx" in command):
            # Tìm package name trong args (phần tử đầu tiên không bắt đầu bằng '-')
            package = next((arg for arg in args if not arg.startswith("-")), None)
            if package:
                try:
                    # Chạy 'npm view' để kiểm tra package có tồn tại không (nhanh hơn info)
                    result = subprocess.run(["npm", "view", package, "name"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"      ✅ Package '{package}' tồn tại trên npm registry.")
                    else:
                        error_msg = result.stderr.strip()
                        if "404" in error_msg:
                            print(f"      ❌ Package '{package}' KHÔNG TỒN TẠI trên npm. Vui lòng kiểm tra lại tên package.")
                        elif "Access token expired" in error_msg:
                            print(f"      ⚠️ Lỗi npm auth (Access token expired), nhưng package có thể vẫn tồn tại.")
                        else:
                            print(f"      ❌ Lỗi khi kiểm tra package '{package}': {error_msg.splitlines()[0] if error_msg else 'Unknown error'}")
                except subprocess.TimeoutExpired:
                    print(f"      ⚠️ Timeout khi kiểm tra package '{package}'.")
                except Exception as e:
                    print(f"      ❌ Lỗi khi kiểm tra package '{package}': {e}")
            else:
                print(f"      ⚠️ Không tìm thấy tên package trong args của '{name}'.")
        else:
            # Kiểm tra xem command có tồn tại không
            try:
                # Dùng which để kiểm tra command
                subprocess.run(["which", command], capture_output=True, check=True)
                print(f"      ✅ Lệnh '{command}' tìm thấy trong hệ thống.")
            except subprocess.CalledProcessError:
                print(f"      ❌ Không tìm thấy lệnh '{command}' trong PATH.")
            except Exception as e:
                print(f"      ⚠️ Không thể xác minh lệnh '{command}': {e}")

if __name__ == "__main__":
    print("=== ANTIGRAVITY DEVOPS ECOSYSTEM HEALTH CHECK ===\n")
    servers = check_mcp_config()
    check_project_structure()
    check_cli_tools()
    validate_mcp_servers(servers)
    print("\n🚀 Kiểm tra hoàn tất!")