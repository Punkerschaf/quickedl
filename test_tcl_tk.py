#!/usr/bin/env python3
"""
Test script to validate setup.py Tcl/Tk detection
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function from setup.py
exec(open('setup.py').read().split('def get_tcl_tk_path():')[1].split('\ndef get_icon_path():')[0])

def test_tcl_tk_detection():
    print("Testing Tcl/Tk detection...")
    
    try:
        # This will execute the get_tcl_tk_path function
        result = eval('get_tcl_tk_path()')
        
        print(f"Found {len(result)} Tcl/Tk entries:")
        for source, dest in result:
            print(f"  {dest} <- {source}")
            if 'tcl' in dest.lower():
                init_tcl = os.path.join(source, 'init.tcl')
                if os.path.exists(init_tcl):
                    print(f"    ✅ init.tcl exists")
                else:
                    print(f"    ❌ init.tcl missing")
        
        return len(result) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tcl_tk_detection()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
