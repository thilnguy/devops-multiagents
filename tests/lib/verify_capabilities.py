#!/usr/bin/env python3
"""
Functional Capability Verification Script
Tests connectivity and availability of all external tools and services.
"""

import subprocess
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional, List, Tuple

# Configuration
DEFAULT_TIMEOUT = 30
RETRY_COUNT = 2
RETRY_DELAY = 2


@dataclass
class TestResult:
    """Result of a capability test."""
    name: str
    success: bool
    message: str
    duration: float
    retries: int = 0
    skipped: bool = False


def test_command(
    name: str,
    command: str,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = RETRY_COUNT,
    required: bool = True
) -> TestResult:
    """
    Test a command with timeout and retry logic.
    
    Args:
        name: Human-readable name of the capability
        command: Shell command to execute
        timeout: Timeout in seconds
        retries: Number of retries on failure
        required: Whether this test is required for overall success
    
    Returns:
        TestResult with success status and details
    """
    print(f"Testing {name}...", end=" ", flush=True)
    
    start_time = time.time()
    last_error = ""
    attempts = 0
    
    for attempt in range(retries + 1):
        attempts = attempt + 1
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                timeout=timeout
            )
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ ({duration:.1f}s)")
                return TestResult(
                    name=name,
                    success=True,
                    message="Connection/syntax successful",
                    duration=duration,
                    retries=attempt
                )
            else:
                last_error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                
        except subprocess.TimeoutExpired:
            last_error = f"Timeout after {timeout}s"
        except Exception as e:
            last_error = str(e)
        
        # Retry if not the last attempt
        if attempt < retries:
            print(f"⚡ Retry {attempt + 1}/{retries}...", end=" ", flush=True)
            time.sleep(RETRY_DELAY)
    
    duration = time.time() - start_time
    # Truncate long error messages
    error_preview = last_error[:100] + "..." if len(last_error) > 100 else last_error
    print(f"❌ Failed: {error_preview}")
    
    return TestResult(
        name=name,
        success=False,
        message=last_error,
        duration=duration,
        retries=attempts - 1
    )


def test_terraform() -> TestResult:
    """Test Terraform CLI and validate configuration."""
    # First check CLI availability
    result = test_command("Terraform CLI", "terraform --version", required=False)
    if not result.success:
        return result
    
    # Check if we can validate terraform config
    tf_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "infra", "terraform")
    if os.path.exists(tf_dir):
        print("Testing Terraform Validate...", end=" ", flush=True)
        start = time.time()
        try:
            # Initialize (without backend)
            init_result = subprocess.run(
                ["terraform", "init", "-backend=false"],
                capture_output=True,
                text=True,
                cwd=tf_dir,
                timeout=60
            )
            if init_result.returncode != 0:
                print(f"❌ Init failed")
                return TestResult(
                    name="Terraform Validate",
                    success=False,
                    message=init_result.stderr.strip(),
                    duration=time.time() - start
                )
            
            # Validate
            validate_result = subprocess.run(
                ["terraform", "validate"],
                capture_output=True,
                text=True,
                cwd=tf_dir,
                timeout=30
            )
            duration = time.time() - start
            
            if validate_result.returncode == 0:
                print(f"✅ ({duration:.1f}s)")
                return TestResult(
                    name="Terraform Validate",
                    success=True,
                    message="Configuration valid",
                    duration=duration
                )
            else:
                print(f"❌ Validation failed")
                return TestResult(
                    name="Terraform Validate",
                    success=False,
                    message=validate_result.stderr.strip(),
                    duration=duration
                )
        except Exception as e:
            print(f"❌ Error: {e}")
            return TestResult(
                name="Terraform Validate",
                success=False,
                message=str(e),
                duration=time.time() - start
            )
    
    return result


def test_kubernetes() -> TestResult:
    """Test Kubernetes connectivity."""
    # Check kubectl availability
    result = test_command("kubectl CLI", "kubectl version --client", required=False)
    if not result.success:
        return result
    
    # Check cluster connectivity
    return test_command(
        "Kubernetes Cluster",
        "kubectl cluster-info --request-timeout=10s",
        timeout=15,
        required=True
    )


def test_jenkins() -> TestResult:
    """Test Jenkins connectivity via MCP or URL."""
    jenkins_url = os.getenv("JENKINS_URL")
    
    if not jenkins_url:
        print("Testing Jenkins Connectivity...", end=" ", flush=True)
        print("⏭️ Skipped (JENKINS_URL not set)")
        return TestResult(
            name="Jenkins Connectivity",
            success=True,
            message="Skipped - JENKINS_URL not configured",
            duration=0,
            skipped=True
        )
    
    # Try to reach Jenkins
    return test_command(
        "Jenkins Connectivity",
        f'curl -s -o /dev/null -w "%{{http_code}}" --max-time 10 {jenkins_url}/login',
        timeout=15,
        required=False
    )


def test_github() -> TestResult:
    """Test GitHub CLI authentication."""
    return test_command(
        "GitHub CLI Auth",
        "gh auth status",
        timeout=10,
        required=False
    )


def test_docker() -> TestResult:
    """Test Docker availability."""
    return test_command(
        "Docker",
        "docker --version",
        timeout=5,
        required=False
    )


def print_summary(results: List[TestResult]) -> int:
    """Print test summary and return exit code."""
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success and not r.skipped]
    skipped = [r for r in results if r.skipped]
    
    total_duration = sum(r.duration for r in results)
    
    print(f"\n📊 Results: {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    
    if failed:
        print("\n❌ Failed tests:")
        for r in failed:
            print(f"   • {r.name}: {r.message[:80]}")
    
    if skipped:
        print("\n⏭️  Skipped tests:")
        for r in skipped:
            print(f"   • {r.name}: {r.message[:80]}")
    
    if not failed:
        print("\n✅ All required capabilities verified!")
        return 0
    else:
        print(f"\n⚠️  {len(failed)} capability test(s) failed.")
        return 1


def verify_all(strict: bool = False) -> int:
    """
    Run all capability verification tests.
    
    Args:
        strict: If True, fail on any test failure (including optional)
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("=" * 60)
    print("FUNCTIONAL CAPABILITY VERIFICATION")
    print("=" * 60)
    print(f"Mode: {'Strict' if strict else 'Normal'}")
    print(f"Timeout: {DEFAULT_TIMEOUT}s, Retries: {RETRY_COUNT}")
    print("=" * 60 + "\n")
    
    results: List[TestResult] = []
    
    # Run all tests
    results.append(test_kubernetes())
    results.append(test_terraform())
    results.append(test_github())
    results.append(test_jenkins())
    results.append(test_docker())
    
    return print_summary(results)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify DevOps capabilities")
    parser.add_argument("--strict", action="store_true", help="Fail on any test failure")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Default timeout in seconds")
    
    args = parser.parse_args()
    DEFAULT_TIMEOUT = args.timeout
    
    exit_code = verify_all(strict=args.strict)
    sys.exit(exit_code)

