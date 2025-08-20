#!/usr/bin/env python3
"""
PyInstaller build script for QuickEDL
Handles local builds for current architecture
"""

import os
import sys
import shutil
import zipfile
import subprocess
import platform
from pathlib import Path
from version import VERSION

def get_platform_info():
    """Get platform and architecture information"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        platform_name = "win"
        arch = "x64" if machine in ["amd64", "x86_64"] else "x86"
    elif system == "darwin":
        platform_name = "macOS"
        # Use uname for reliable architecture detection
        try:
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            actual_arch = result.stdout.strip().lower()
            if actual_arch in ["arm64", "aarch64"]:
                arch = "arm64"
            else:
                arch = "x86_64"
        except Exception:
            # Fallback
            if machine in ["arm64", "aarch64"] or "arm" in machine:
                arch = "arm64"
            else:
                arch = "x86_64"
    else:
        platform_name = "linux"
        arch = "x64" if machine in ["x86_64", "amd64"] else machine
    
    return platform_name, arch

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name} directory")

def build_with_pyinstaller():
    """Build executable using PyInstaller"""
    platform_name, arch = get_platform_info()
    
    print(f"🏗️  Building QuickEDL {VERSION} for {platform_name} {arch}")
    print(f"🐍 Python: {sys.executable}")
    print(f"📍 Platform: {platform.platform()}")
    
    # Set up environment for architecture-specific builds
    env = os.environ.copy()
    
    if sys.platform == "darwin":
        if arch == "arm64":
            env["ARCHFLAGS"] = "-arch arm64"
            env["_PYTHON_HOST_PLATFORM"] = "macosx-11.0-arm64"
            print("🔧 Targeting ARM64 architecture")
        else:
            env["ARCHFLAGS"] = "-arch x86_64"
            env["_PYTHON_HOST_PLATFORM"] = "macosx-10.9-x86_64"
            print("🔧 Targeting Intel x86_64 architecture")
    
    # Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "quickedl.spec", "--clean", "--noconfirm"]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Build failed!")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    
    print("✅ Build completed successfully!")
    return True

def package_windows():
    """Package Windows executable into zip"""
    platform_name, arch = get_platform_info()
    
    exe_path = Path("dist/quickedl.exe")
    if not exe_path.exists():
        print("❌ Windows executable not found!")
        return False
    
    # Create zip package
    zip_name = f"quickedl_{VERSION}_{platform_name}{arch}.zip"
    zip_path = Path("dist") / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(exe_path, "quickedl.exe")
        
        # Add any additional files if needed
        # zipf.write("README.md", "README.md")
    
    print(f"📦 Windows package created: {zip_path}")
    return True

def package_macos():
    """Package macOS app bundle into DMG"""
    platform_name, arch = get_platform_info()
    
    app_path = Path("dist/QuickEDL.app")
    if not app_path.exists():
        print("❌ macOS app bundle not found!")
        if Path("dist").exists():
            print(f"📁 Available files in dist/: {list(Path('dist').iterdir())}")
        return False
    
    print(f"📱 Found app bundle: {app_path}")
    
    # Create DMG
    dmg_name = f"quickedl_{VERSION}_{platform_name}_{arch}.dmg"
    dmg_path = Path("dist") / dmg_name
    
    try:
        # Create DMG using hdiutil
        cmd = [
            "hdiutil", "create",
            "-volname", "QuickEDL",
            "-srcfolder", str(app_path),
            "-ov", "-format", "UDZO",
            str(dmg_path)
        ]
        
        print(f"📀 Creating DMG: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"📦 DMG package created: {dmg_path}")
            return True
        else:
            print(f"❌ DMG creation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ hdiutil not found - cannot create DMG on this system")
        return False

def verify_build():
    """Verify the built application"""
    if sys.platform == "darwin":
        app_path = Path("dist/QuickEDL.app")
        if app_path.exists():
            print(f"🔍 Verifying app bundle: {app_path}")
            
            # Check executable
            executable = app_path / "Contents/MacOS/quickedl"
            if executable.exists():
                print(f"✅ Executable found: {executable}")
                
                # Check architecture
                try:
                    result = subprocess.run(["file", str(executable)], capture_output=True, text=True)
                    print(f"🏗️  Architecture: {result.stdout.strip()}")
                    
                    result = subprocess.run(["lipo", "-info", str(executable)], capture_output=True, text=True)
                    print(f"🔧 Lipo info: {result.stdout.strip()}")
                except FileNotFoundError:
                    print("⚠️  Could not check architecture (file/lipo not found)")
            else:
                print(f"❌ Executable not found at: {executable}")
                
            # Check Info.plist
            plist_path = app_path / "Contents/Info.plist"
            if plist_path.exists():
                print(f"✅ Info.plist found: {plist_path}")
            else:
                print(f"❌ Info.plist not found at: {plist_path}")
    
    elif sys.platform == "win32":
        exe_path = Path("dist/quickedl.exe")
        if exe_path.exists():
            print(f"✅ Windows executable found: {exe_path}")
            print(f"📏 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print(f"❌ Windows executable not found at: {exe_path}")

def main():
    """Main build process"""
    print("🚀 QuickEDL PyInstaller Build")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build with PyInstaller
    if not build_with_pyinstaller():
        sys.exit(1)
    
    # Verify build
    verify_build()
    
    # Package based on platform
    success = False
    if sys.platform == "win32":
        success = package_windows()
    elif sys.platform == "darwin":
        success = package_macos()
    else:
        print("⚠️  Linux packaging not implemented yet")
        success = True  # Build succeeded, just no packaging
    
    if success:
        print("\n🎉 Build and packaging completed successfully!")
        
        # Show final output
        if Path("dist").exists():
            print("\n📁 Final output files:")
            for item in Path("dist").iterdir():
                if item.is_file():
                    size = item.stat().st_size / 1024 / 1024
                    print(f"   📄 {item.name} ({size:.1f} MB)")
                elif item.is_dir():
                    print(f"   📁 {item.name}/")
    else:
        print("\n❌ Packaging failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
