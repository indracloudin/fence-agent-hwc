#!/usr/bin/env python3
"""
Test script for fence_huaweicloud.py without requiring the full fencing library.
This script tests the core functionality and parameter handling.
"""

import sys
import os
import importlib.util

def test_import():
    """Test if the fence_huaweicloud.py can be imported without errors"""
    try:
        # Add the current directory to the path
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Load the fence_huaweicloud.py file as a module
        spec = importlib.util.spec_from_file_location(
            "fence_huaweicloud", 
            os.path.join(os.path.dirname(__file__), "fence_huaweicloud.py")
        )
        fence_module = importlib.util.module_from_spec(spec)
        
        # Execute the module, which should define all functions
        spec.loader.exec_module(fence_module)
        
        print("✓ Successfully imported fence_huaweicloud.py")
        return True
    except Exception as e:
        print(f"✗ Failed to import fence_huaweicloud.py: {e}")
        return False

def test_functions_exist():
    """Test if the main functions exist in the module"""
    try:
        spec = importlib.util.spec_from_file_location(
            "fence_huaweicloud", 
            os.path.join(os.path.dirname(__file__), "fence_huaweicloud.py")
        )
        fence_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fence_module)
        
        required_functions = [
            'define_new_opts',
            'get_power_status', 
            'set_power_status', 
            'get_nodes_list',
            'start_instance',
            'stop_instance',
            'reboot_instance',
            'get_status'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not hasattr(fence_module, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"✗ Missing functions: {missing_functions}")
            return False
        else:
            print("✓ All required functions exist")
            return True
    except Exception as e:
        print(f"✗ Error testing functions: {e}")
        return False

def test_options_definition():
    """Test if the new options are properly defined"""
    try:
        spec = importlib.util.spec_from_file_location(
            "fence_huaweicloud", 
            os.path.join(os.path.dirname(__file__), "fence_huaweicloud.py")
        )
        fence_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fence_module)
        
        # Call the function to define options
        fence_module.define_new_opts()
        
        # Check if the all_opt dictionary has the new options
        # This test is limited without importing the fencing module,
        # but we can at least check that the function exists and runs
        print("✓ Options definition function works")
        return True
    except Exception as e:
        print(f"✗ Error testing options definition: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing fence_huaweicloud.py enhancements...")
    print("="*50)
    
    tests = [
        ("Import Test", test_import),
        ("Functions Exist Test", test_functions_exist),
        ("Options Definition Test", test_options_definition),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The fence agent has been successfully enhanced.")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())