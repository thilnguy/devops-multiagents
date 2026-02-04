#!/usr/bin/env python3
"""
Docker Architecture Validator
-----------------------------
Validates that Docker images support ARM64 architecture for Graviton deployment.
Usage: python3 validate_docker_arch.py <image:tag>
"""

import subprocess
import sys
import json
import argparse

def get_image_platforms(image: str) -> list:
    """Get supported platforms for a Docker image."""
    try:
        # Try to inspect manifest
        result = subprocess.run(
            ["docker", "manifest", "inspect", image],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # Fallback: try docker image inspect for local images
            result = subprocess.run(
                ["docker", "image", "inspect", image, "--format", "{{.Architecture}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return [f"linux/{result.stdout.strip()}"]
            return []
        
        manifest = json.loads(result.stdout)
        
        # Handle manifest list (multi-arch) or single manifest
        if "manifests" in manifest:
            platforms = []
            for m in manifest["manifests"]:
                platform = m.get("platform", {})
                os_name = platform.get("os", "linux")
                arch = platform.get("architecture", "unknown")
                variant = platform.get("variant", "")
                platform_str = f"{os_name}/{arch}"
                if variant:
                    platform_str += f"/{variant}"
                platforms.append(platform_str)
            return platforms
        else:
            # Single manifest
            arch = manifest.get("architecture", "unknown")
            return [f"linux/{arch}"]
            
    except subprocess.TimeoutExpired:
        print(f"Error: Timeout inspecting image {image}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON from manifest inspect")
        return []
    except FileNotFoundError:
        print("Error: Docker CLI not found")
        return []

def validate_arm64_support(images: list) -> dict:
    """Validate ARM64 support for a list of images."""
    results = {}
    
    for image in images:
        platforms = get_image_platforms(image)
        
        # Check for ARM64 support
        has_arm64 = any("arm64" in p or "aarch64" in p for p in platforms)
        has_amd64 = any("amd64" in p or "x86_64" in p for p in platforms)
        
        results[image] = {
            "platforms": platforms,
            "arm64": has_arm64,
            "amd64": has_amd64,
            "multi_arch": has_arm64 and has_amd64
        }
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Validate Docker Image ARM64 Support")
    parser.add_argument("images", nargs="+", help="Docker images to validate (e.g., nginx:alpine)")
    parser.add_argument("--strict", action="store_true", help="Exit with error if any image lacks ARM64")
    
    args = parser.parse_args()
    
    print("🔍 Validating Docker Image Architectures...")
    print("")
    
    results = validate_arm64_support(args.images)
    
    all_pass = True
    for image, info in results.items():
        if info["arm64"]:
            status = "✅"
        else:
            status = "❌"
            all_pass = False
        
        multi = "Multi-Arch" if info["multi_arch"] else "Single-Arch"
        print(f"{status} {image} ({multi})")
        print(f"   Platforms: {', '.join(info['platforms']) or 'Unknown'}")
        print("")
    
    if all_pass:
        print("✅ All images support ARM64!")
        sys.exit(0)
    else:
        print("⚠️ Some images do not support ARM64. Deployment to Graviton may fail.")
        if args.strict:
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    main()
