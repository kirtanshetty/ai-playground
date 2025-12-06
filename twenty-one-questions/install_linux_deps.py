#!/usr/bin/env python3
"""
Install Python dependencies for AWS Lambda (Linux) on macOS/other platforms.
Uses pip's --platform flag to download Linux-compatible wheels.
"""

import subprocess
import sys
import os


def install_linux_deps(requirements_file, target_dir):
    """
    Install dependencies for Linux platform.
    
    Args:
        requirements_file: Path to requirements.txt
        target_dir: Directory to install packages to
    """
    # Lambda runs on Amazon Linux 2, which is compatible with manylinux2014
    platform = "manylinux2014_x86_64"
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Install packages with Linux platform flag
    # Use --only-binary=:all: to force binary wheels (no source builds)
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", requirements_file,
        "-t", target_dir,
        "--platform", platform,
        "--only-binary=:all:",
        "--python-version", "3.11",
        "--implementation", "cp",
        "--upgrade",
        "--no-cache-dir",
    ]
    
    print(f"Installing packages for Linux platform ({platform})...")
    print(f"Target directory: {target_dir}")
    
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: pip install returned non-zero exit code: {result.returncode}")
            if result.stderr:
                print(f"stderr: {result.stderr}")
            if result.stdout:
                print(f"stdout: {result.stdout}")
            
            # Try alternative: use linux_x86_64 platform
            print("\nTrying alternative platform (linux_x86_64)...")
            cmd_alt = [
                sys.executable, "-m", "pip", "install",
                "-r", requirements_file,
                "-t", target_dir,
                "--platform", "linux_x86_64",
                "--only-binary=:all:",
                "--python-version", "3.11",
                "--implementation", "cp",
                "--upgrade",
                "--no-cache-dir",
            ]
            result_alt = subprocess.run(cmd_alt, check=False, capture_output=True, text=True)
            
            if result_alt.returncode != 0:
                print(f"Alternative platform also failed: {result_alt.returncode}")
                if result_alt.stderr:
                    print(f"stderr: {result_alt.stderr}")
        
        print("Installation completed.")
        
    except Exception as e:
        print(f"Error installing packages: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: install_linux_deps.py <requirements.txt> <target_dir>")
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    target_dir = sys.argv[2]
    
    if not os.path.exists(requirements_file):
        print(f"Error: Requirements file not found: {requirements_file}")
        sys.exit(1)
    
    install_linux_deps(requirements_file, target_dir)

