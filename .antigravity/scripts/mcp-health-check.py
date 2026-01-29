import os
import json
import subprocess

def check_mcp_config():
    """Kiểm tra file cấu hình MCP của hệ thống"""
    # Đường dẫn mặc định thường gặp trên Mac
    config_path = os.path.expanduser("~/Library/Application Support/antigravity/mcp_config.json")
    
    print("🔍 [1/3] Kiểm tra file cấu hình MCP...")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            servers = config.get("mcpServers", {})
            print(f"✅ Tìm thấy {len(servers)} servers được cấu hình: {', '.join(servers.keys())}")
            return servers
    else:
        print("❌ Không tìm thấy file mcp_config.json. Hãy kiểm tra cài đặt App.")
        return None

def check_project_structure():
    """Kiểm tra các Persona và Skill đã được định nghĩa chưa"""
    print("\n🔍 [2/3] Kiểm tra cấu trúc Project .antigravity/...")
    required_dirs = [".antigravity/personas", ".antigravity/skills"]
    for d in required_dirs:
        if os.path.exists(d):
            files = os.listdir(d)
            print(f"✅ {d}: {len(files)} files sẵn sàng.")
        else:
            print(f"⚠️ Thiếu thư mục: {d}")

def check_cli_tools():
    """Kiểm tra các công cụ dòng lệnh mà MCP phụ thuộc vào"""
    print("\n🔍 [3/3] Kiểm tra CLI Tools (Dependencies)...")
    tools = ["gh", "aws", "terraform"]
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"✅ {tool.upper()} đã được cài đặt.")
        except:
            print(f"❌ {tool.upper()} chưa được cài đặt hoặc chưa thêm vào PATH.")

if __name__ == "__main__":
    print("=== ANTIGRAVITY DEVOPS ECOSYSTEM HEALTH CHECK ===\n")
    servers = check_mcp_config()
    check_project_structure()
    check_cli_tools()
    print("\n🚀 Hệ thống đã sẵn sàng để 'Vibe'!")