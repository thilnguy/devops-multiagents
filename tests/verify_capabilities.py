import subprocess
import os

def test_command(name, command):
    print(f"Testing {name}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {name} connection/syntax successful.")
            return True
        else:
            print(f"❌ {name} failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
        return False

def verify_all():
    print("=== FUNCTIONAL CAPABILITY VERIFICATION ===\n")
    
    # 1. K8s Connectivity
    test_command("Kubernetes Cluster", "kubectl get nodes")
    
    # 2. Terraform Syntax/Init check
    # Note: Requires a terraform directory to be effective, but we checking CLI availability/path
    test_command("Terraform CLI", "terraform --version")
    
    # 3. Jenkins Connectivity (Ping URL if provided)
    # This is a placeholder as we don't have the real URL yet
    print("Testing Jenkins Connectivity (Skipped - Needs real URL)...")

    # 4. GitHub Auth check
    test_command("GitHub CLI Auth", "gh auth status")

    print("\nVerification Complete.")

if __name__ == "__main__":
    verify_all()
