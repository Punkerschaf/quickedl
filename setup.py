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
    ],
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# Platform specific options
if sys.platform == "win32":
    # Windows specific options
    build_exe_options.update({
        "include_msvcrt": False
    })
# No special options needed for macOS and Linux with cx_Freeze

setup(
    name="QuickEDL",
    version=VERSION,
    description="QuickEDL - EDL creation tool",
    author="Eric Kirchheim",
    options={"build_exe": build_exe_options},
    executables=[executable]
)
