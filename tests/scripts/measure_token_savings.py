#!/usr/bin/env python3
"""
Token Savings Benchmark
Measures the reduction in context size (estimated by char count)
achieved by Smart Context Tools.
"""

import os
import json
import subprocess
import sys

# Paths
SCRIPTS_DIR = "scripts"
ANALYZE_LOGS = os.path.join(SCRIPTS_DIR, "analyze_logs.py")
SUMMARIZE_INFRA = os.path.join(SCRIPTS_DIR, "summarize_infra.py")
TEMP_DIR = "/tmp/benchmark"

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def generate_dummy_log(filepath, lines=2000):
    """Generates a noisy log file with repetitive patterns."""
    print(f"[1/4] Generating dummy log ({lines} lines)...")
    with open(filepath, 'w') as f:
        # Pattern 1: Connection Refused (Heavy noise)
        for i in range(int(lines * 0.8)):
            f.write(f"2024-01-01 10:{i%60:02d}:{i%60:02d} [ERROR] Connection refused to db-primary-shard-{i%5}\n")
        # Pattern 2: Application Stack Trace (Generic)
        for i in range(int(lines * 0.1)):
            f.write(f"2024-01-01 11:00:00 [CRITICAL] NullPointerException at Service.java:42 (Request ID: {i})\n")
        # Pattern 3: Random Info
        for i in range(int(lines * 0.1)):
            f.write(f"2024-01-01 12:00:00 [INFO] Health check passed\n")

def generate_dummy_state(filepath):
    """Generates a large dummy terraform state."""
    print(f"[2/4] Generating dummy terraform state...")
    resources = []
    # Generate 50 similar EC2 instances
    for i in range(50):
        resources.append({
            "type": "aws_instance",
            "name": f"worker-node-{i}",
            "mode": "managed",
            "instances": [{
                "attributes": {
                    "id": f"i-0123456789abc{i:03d}",
                    "ami": "ami-0c55b159cbfafe1f0",
                    "instance_type": "t3.medium",
                    "private_ip": f"10.0.1.{i}",
                    "public_ip": f"34.200.1.{i}",
                    "tags": {"Name": f"worker-{i}", "Env": "prod", "Owner": "devops"},
                    "root_block_device": [{"volume_size": 20, "volume_type": "gp3"}]
                }
            }]
        })
    
    state = {
        "version": 4,
        "terraform_version": "1.5.0",
        "resources": resources
    }
    
    with open(filepath, 'w') as f:
        json.dump(state, f, indent=2)

def measure_reduction(raw_file, command):
    """Runs command and compares output size vs raw file size."""
    # Measure Raw
    with open(raw_file, 'r') as f:
        raw_content = f.read()
    raw_len = len(raw_content)
    
    # Run Tool
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=True
    )
    
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}")
        return 0, 0, 0
        
    output_len = len(result.stdout)
    reduction = (1 - (output_len / raw_len)) * 100
    
    return raw_len, output_len, reduction

def main():
    ensure_dir(TEMP_DIR)
    log_file = os.path.join(TEMP_DIR, "bench.log")
    state_file = os.path.join(TEMP_DIR, "terraform.tfstate")
    
    # 1. Log Benchmark
    generate_dummy_log(log_file)
    raw_log, smart_log, log_saved = measure_reduction(
        log_file, 
        f"python3 {ANALYZE_LOGS} {log_file}"
    )
    
    # 2. Infra Benchmark
    generate_dummy_state(state_file)
    # Mocking summarize_infra to read this file implies passing the dir
    raw_state, smart_state, state_saved = measure_reduction(
        state_file,
        f"python3 {SUMMARIZE_INFRA} {TEMP_DIR}"
    )

    print("\n" + "="*60)
    print("TOKEN EFFICIENCY BENCHMARK RESULTS")
    print("="*60)
    
    print(f"\n📄 LOG ANALYSIS (2000 lines)")
    print(f"   Raw Size:     {raw_log} chars (~{raw_log//4} tokens)")
    print(f"   Smart output: {smart_log} chars (~{smart_log//4} tokens)")
    print(f"   SAVINGS:      {log_saved:.2f}% 🚀")

    print(f"\n🏗️ INFRA STRUCTURE (50 Resources)")
    print(f"   Raw Size:     {raw_state} chars (~{raw_state//4} tokens)")
    print(f"   Smart output: {smart_state} chars (~{smart_state//4} tokens)")
    print(f"   SAVINGS:      {state_saved:.2f}% 🚀")
    
    print("\n" + "="*60)

    # Cleanup
    os.remove(log_file)
    os.remove(state_file)
    os.rmdir(TEMP_DIR)

if __name__ == "__main__":
    main()
