#!/usr/bin/env python3
"""
Launch script for Power Platform Utility

This script provides an easy way to launch the application with proper
environment setup and error handling.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PySide6
        print(f"✓ PySide6 {PySide6.__version__} found")
        return True
    except ImportError:
        print("✗ PySide6 not found. Please install dependencies:")
        print("  pip install -r requirements.txt")
        return False

def check_pac_cli():
    """Check if PAC CLI is available."""
    try:
        result = subprocess.run(
            ["pac", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ PAC CLI found: {result.stdout.strip()}")
            return True
        else:
            print("✗ PAC CLI not accessible")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ PAC CLI not found. Please install Power Platform CLI:")
        print("  winget install Microsoft.PowerPlatformCLI")
        return False

def main():
    """Main launch function."""
    print("Power Platform Utility - Launch Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check PAC CLI (optional but recommended)
    if not check_pac_cli():
        print("\nWarning: PAC CLI not found. Some features may not work.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Starting Power Platform Utility...")
    print("=" * 50)
    
    # Launch the application
    try:
        # Add src to Python path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        # Import and run main
        from main import main as app_main
        app_main()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError launching application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
