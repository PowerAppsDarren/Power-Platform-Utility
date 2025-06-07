#!/usr/bin/env python3
"""
Test script for PAC CLI integration

This script tests the PAC CLI wrapper functionality without launching the full GUI.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.pac_cli import PACCLIWrapper, PACCLIError
from core.environment import EnvironmentManager
from utils.helpers import setup_logging

def test_pac_cli_basic():
    """Test basic PAC CLI functionality."""
    print("Testing PAC CLI basic functionality...")
    
    try:
        pac_cli = PACCLIWrapper()
        print("✓ PAC CLI wrapper initialized successfully")
        
        # Test a simple command
        result = pac_cli.run_command(["--version"])
        if result["success"]:
            print(f"✓ PAC CLI version: {result['stdout'].strip()}")
        else:
            print(f"✗ Failed to get PAC CLI version: {result['stderr']}")
            return False
            
        return True
        
    except PACCLIError as e:
        print(f"✗ PAC CLI Error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_environment_manager():
    """Test environment manager functionality."""
    print("\nTesting Environment Manager...")
    
    try:
        pac_cli = PACCLIWrapper()
        env_manager = EnvironmentManager(pac_cli)
        print("✓ Environment manager initialized successfully")
        
        # Note: This will fail if not authenticated, which is expected
        print("Note: Environment listing requires authentication")
        
        return True
        
    except Exception as e:
        print(f"✗ Environment manager error: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting Configuration...")
    
    try:
        from utils.helpers import load_config
        config = load_config()
        print("✓ Configuration loaded successfully")
        print(f"  - Application: {config['application']['name']}")
        print(f"  - Version: {config['application']['version']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {str(e)}")
        return False

def test_logging():
    """Test logging setup."""
    print("\nTesting Logging...")
    
    try:
        setup_logging("DEBUG")
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Test log message")
        print("✓ Logging setup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Power Platform Utility - Integration Test")
    print("=" * 50)
    
    tests = [
        ("PAC CLI Basic", test_pac_cli_basic),
        ("Environment Manager", test_environment_manager),
        ("Configuration", test_configuration),
        ("Logging", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
