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
        # GitHub Actions and local Python installations
        python_versions = glob.glob("/Library/Frameworks/Python.framework/Versions/*/")
        python_versions.extend(glob.glob("/opt/hostedtoolcache/Python/*/*/"))
        
        for version_path in python_versions:
            tcl_path = os.path.join(version_path, "lib", "tcl8.6")
            tk_path = os.path.join(version_path, "lib", "tk8.6")
            
            if os.path.exists(tcl_path):
                tcl_tk_files.append((tcl_path, "lib/tcl8.6"))
            if os.path.exists(tk_path):
                tcl_tk_files.append((tk_path, "lib/tk8.6"))
        
        # Homebrew installations
        homebrew_paths = [
            ("/opt/homebrew/lib/tcl8.6", "lib/tcl8.6"),
            ("/opt/homebrew/lib/tk8.6", "lib/tk8.6"),
            ("/usr/local/lib/tcl8.6", "lib/tcl8.6"),
            ("/usr/local/lib/tk8.6", "lib/tk8.6"),
        ]
        
        for path, dest in homebrew_paths:
            if os.path.exists(path):
                tcl_tk_files.append((path, dest))
        
        # System frameworks (fallback)
        system_paths = [
            ("/System/Library/Frameworks/Tcl.framework/Versions/8.6/Resources/Scripts", "lib/tcl8.6"),
            ("/System/Library/Frameworks/Tk.framework/Versions/8.6/Resources/Scripts", "lib/tk8.6")
        ]
        for path, dest in system_paths:
            if os.path.exists(path):
                tcl_tk_files.append((path, dest))
    
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
