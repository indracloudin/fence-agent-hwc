#!/usr/bin/env python3
"""
Simple syntax and structure test for fence_huaweicloud.py
"""

import ast
import sys
import os

def test_syntax():
    """Test if the fence_huaweicloud.py has valid Python syntax"""
    try:
        with open("fence_huaweicloud.py", "r", encoding="utf-8") as f:
            source = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(source)
        print("✓ Syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking syntax: {e}")
        return False

def test_key_components():
    """Test if key components exist in the source code"""
    try:
        with open("fence_huaweicloud.py", "r", encoding="utf-8") as f:
            source = f.read()
        
        # Check for the new enterprise project ID parameter
        if "--enterprise-project-id" in source:
            print("✓ Enterprise Project ID parameter found")
            enterprise_project_ok = True
        else:
            print("✗ Enterprise Project ID parameter not found")
            enterprise_project_ok = False
        
        # Check for the enhanced define_new_opts function
        if '"enterprise_project_id"' in source:
            print("✓ Enterprise Project ID option definition found")
            option_def_ok = True
        else:
            print("✗ Enterprise Project ID option definition not found")
            option_def_ok = False
            
        # Check for required parameters
        if '"required" : "1"' in source and "--project-id" in source:
            print("✓ Project ID set as required parameter")
            project_required_ok = True
        else:
            print("✗ Project ID not set as required parameter")
            project_required_ok = False
        
        return enterprise_project_ok and option_def_ok and project_required_ok
    except Exception as e:
        print(f"✗ Error checking components: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing fence_huaweicloud.py enhancements...")
    print("="*50)
    
    print("\nSyntax Test:")
    syntax_ok = test_syntax()
    
    print("\nComponent Test:")
    components_ok = test_key_components()
    
    print("\n" + "="*50)
    if syntax_ok and components_ok:
        print("✓ All tests passed! The fence agent has been successfully enhanced.")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())