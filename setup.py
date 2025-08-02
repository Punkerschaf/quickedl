"""
This file is part of QuickEDL.
It defines the build configuration for the application using cx_Freeze.
"""
import sys
import os
from cx_Freeze import setup, Executable

# Import version
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version import VERSION

def get_tcl_tk_path():
    """Get the path to Tcl/Tk libraries"""
    import glob
    import platform
    
    tcl_tk_files = []
    
    if platform.system() == "Darwin":  # macOS
        # Priority order: Homebrew -> Python Framework -> System
        search_paths = []
        
        # 1. Homebrew installations (preferred)
        if platform.machine() == "arm64":  # Apple Silicon
            search_paths.extend([
                "/opt/homebrew/lib",
                "/opt/homebrew/Cellar/tcl-tk/*/lib"
            ])
        else:  # Intel
            search_paths.extend([
                "/usr/local/lib",
                "/usr/local/Cellar/tcl-tk/*/lib"
            ])
        
        # 2. Python Framework installations
        search_paths.extend([
            "/Library/Frameworks/Python.framework/Versions/*/lib",
            "/opt/hostedtoolcache/Python/*/*/lib"  # GitHub Actions
        ])
        
        # 3. System frameworks (fallback)
        search_paths.extend([
            "/System/Library/Frameworks/Tcl.framework/Versions/*/Resources",
            "/System/Library/Frameworks/Tk.framework/Versions/*/Resources"
        ])
        
        # Find Tcl/Tk directories
        for pattern in search_paths:
            for base_path in glob.glob(pattern):
                tcl_path = os.path.join(base_path, "tcl8.6")
                tk_path = os.path.join(base_path, "tk8.6")
                
                if os.path.exists(tcl_path) and os.path.exists(os.path.join(tcl_path, "init.tcl")):
                    tcl_tk_files.append((tcl_path, "lib/tcl8.6"))
                    print(f"Found Tcl: {tcl_path}")
                    
                if os.path.exists(tk_path):
                    tcl_tk_files.append((tk_path, "lib/tk8.6"))
                    print(f"Found Tk: {tk_path}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for item in tcl_tk_files:
            if item not in seen:
                seen.add(item)
                unique_files.append(item)
        tcl_tk_files = unique_files
    
    print(f"Tcl/Tk files to include: {tcl_tk_files}")
    return tcl_tk_files

def get_icon_path():
    """Get the appropriate icon path for the current platform"""
    if sys.platform == "win32":
        return "resources/icon_win.ico"
    elif sys.platform == "darwin":
        return "resources/icon_mac.icns"
    else:
        return "resources/icon_unix.png"

# Determine the base for the executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # No console window for Windows

# Define the executable
executable = Executable(
    script="main.py",
    base=base,
    target_name="QuickEDL" + (".exe" if sys.platform == "win32" else ""),
    icon=get_icon_path()
)

# Build options
build_exe_options = {
    "packages": [
        "tkinter", 
        "ttkbootstrap", 
        "yaml", 
        "pathlib",
        "logging",
        "datetime",
        "settings",
        "projects"
    ],
    "excludes": [
        "tkinter.test",
        "unittest",
        "test",
        "distutils",
        "lib2to3"
    ],
    "include_files": [
        ("resources/", "resources/"),
    ] + get_tcl_tk_path(),
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# Platform specific options
if sys.platform == "darwin":
    # macOS specific options for better compatibility
    build_exe_options.update({
        "silent": True,
        # Add environment variables for Tcl/Tk
        "environment": {
            "TCL_LIBRARY": "",  # Will be set by wrapper
            "TK_LIBRARY": "",   # Will be set by wrapper
        }
    })

# No special options needed for Windows and Linux with cx_Freeze

setup(
    name="QuickEDL",
    version=VERSION,
    description="QuickEDL - EDL creation tool",
    author="Eric Kirchheim",
    options={"build_exe": build_exe_options},
    executables=[executable]
)
