#!/usr/bin/env python3
"""
QuickEDL Build Script for PyInstaller
Cross-platform build automation for Windows and macOS
"""

import os
import sys
import shutil
import subprocess
import zipfile
import platform
from pathlib import Path

# Import version
sys.path.insert(0, os.path.dirname(__file__))
from version import VERSION

def get_platform_info():
    """Get platform and architecture information"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        return "winx64", ""
    elif system == "darwin":
        # Check for explicit architecture override from environment
        if os.environ.get("ARCHFLAGS") == "-arch x86_64":
            return "macOS", "_x86_64"
        elif os.environ.get("ARCHFLAGS") == "-arch arm64":
            return "macOS", "_arm64"
        
        # Auto-detect based on machine type
        if machine in ["arm64", "aarch64"]:
            return "macOS", "_arm64"
        else:
            return "macOS", "_x86_64"
    else:
        return system, f"_{machine}"

def clean_build_dirs():
    """Clean previous build artifacts"""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def get_spec_file():
    """Get the spec file path"""
    spec_file = "quickedl.spec"
    if not os.path.exists(spec_file):
        print(f"Error: {spec_file} not found!")
        sys.exit(1)
    return spec_file

def build_with_pyinstaller():
    """Build the application using PyInstaller"""
    spec_file = get_spec_file()
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        spec_file
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Build failed!")
        print(result.stderr)
        sys.exit(1)
    
    print("Build completed successfully!")

def package_windows():
    """Package Windows executable into ZIP"""
    platform_name, arch = get_platform_info()
    
    exe_path = Path("dist/quickedl.exe")
    if not exe_path.exists():
        print("Windows executable not found!")
        return False
    
    # Create zip package
    zip_name = f"quickedl_{VERSION}_{platform_name}{arch}.zip"
    zip_path = Path("dist") / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(exe_path, "quickedl.exe")
        
        # Add any additional files if needed
        # zipf.write("README.md", "README.md")
    
    print(f"Windows package created: {zip_path}")
    return True

def package_macos():
    """Package macOS app bundle into DMG"""
    platform_name, arch = get_platform_info()
    
    app_path = Path("dist/QuickEDL.app")
    if not app_path.exists():
        print("macOS app bundle not found!")
        if Path("dist").exists():
            print(f"Available files in dist/: {list(Path('dist').iterdir())}")
        return False
    
    print(f"Found app bundle: {app_path}")
    
    # Create DMG
    dmg_name = f"quickedl_{VERSION}_{platform_name}_{arch}.dmg"
    dmg_path = Path("dist") / dmg_name
    
    # Remove existing DMG if it exists
    if dmg_path.exists():
        dmg_path.unlink()
    
    # Use hdiutil to create DMG (macOS only)
    try:
        cmd = [
            "hdiutil", "create",
            "-volname", "QuickEDL",
            "-srcfolder", str(app_path),
            "-ov",
            "-format", "UDZO",
            str(dmg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"DMG package created: {dmg_path}")
            return True
        else:
            print(f"DMG creation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("hdiutil not found - cannot create DMG on this system")
        return False

def verify_build():
    """Verify the build results"""
    platform_name, arch = get_platform_info()
    
    if platform_name.startswith("macOS"):
        app_path = Path("dist/QuickEDL.app")
        if app_path.exists():
            print(f"Verifying app bundle: {app_path}")
            
            # Check executable
            executable = app_path / "Contents/MacOS/quickedl"
            if executable.exists():
                # Check architecture using 'file' command
                result = subprocess.run(["file", str(executable)], capture_output=True, text=True)
                print(f"Executable found: {executable}")
                print(f"Architecture: {result.stdout.strip()}")
                
                # Check with lipo for detailed arch info
                result = subprocess.run(["lipo", "-info", str(executable)], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Architecture details: {result.stdout.strip()}")
            else:
                print(f"Executable not found at: {executable}")
                return False
                
            # Check Info.plist
            plist_path = app_path / "Contents/Info.plist"
            if plist_path.exists():
                print(f"Info.plist found: {plist_path}")
            else:
                print(f"Info.plist not found at: {plist_path}")
                
    elif platform_name == "winx64":
        exe_path = Path("dist/quickedl.exe")
        if exe_path.exists():
            print(f"Windows executable found: {exe_path}")
        else:
            print(f"Windows executable not found at: {exe_path}")
            return False
    
    return True

def main():
    """Main build process"""
    print("QuickEDL PyInstaller Build")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build with PyInstaller
    build_with_pyinstaller()
    
    # Verify build
    if not verify_build():
        print("Build verification failed!")
        sys.exit(1)
    
    # Platform-specific packaging
    platform_name, _ = get_platform_info()
    
    success = False
    if platform_name == "winx64":
        success = package_windows()
    elif platform_name.startswith("macOS"):
        success = package_macos()
    else:
        print(f"Packaging not implemented for platform: {platform_name}")
        success = True  # Don't fail for unsupported packaging
    
    if success:
        print("\nBuild and packaging completed successfully!")
        
        # List final artifacts
        dist_path = Path("dist")
        if dist_path.exists():
            print(f"\nCreated files in {dist_path}:")
            for item in dist_path.iterdir():
                if item.is_file():
                    size = item.stat().st_size / (1024 * 1024)  # MB
                    print(f"  {item.name} ({size:.1f} MB)")
    else:
        print("\nPackaging failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
