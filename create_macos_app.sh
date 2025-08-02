#!/bin/bash
# Script to create macOS .app bundle from cx_Freeze output

BUILD_DIR="build"
APP_NAME="QuickEDL"
VERSION=$(python -c "from version import VERSION; print(VERSION)")
# Create a macOS-compatible version (replace problematic characters)
BUNDLE_VERSION=$(echo "$VERSION" | sed 's/-\(alpha\|beta\|rc\|.*\).*//g')

# Ensure we have at least 3 version components (e.g., 3.0.0)
if [[ "$BUNDLE_VERSION" =~ ^[0-9]+\.[0-9]+$ ]]; then
    BUNDLE_VERSION="${BUNDLE_VERSION}.0"
elif [[ "$BUNDLE_VERSION" =~ ^[0-9]+$ ]]; then
    BUNDLE_VERSION="${BUNDLE_VERSION}.0.0"
fi

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "Error: Build directory not found. Run 'python setup.py build' first."
    exit 1
fi

# Find the executable in build directory
EXE_DIR=$(find "$BUILD_DIR" -name "exe.*" -type d | head -1)
if [ ! -d "$EXE_DIR" ]; then
    echo "Error: Executable directory not found in build."
    exit 1
fi

# Create .app bundle structure
APP_BUNDLE="dist/${APP_NAME}.app"
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Copy executable and resources
cp -r "$EXE_DIR/"* "$APP_BUNDLE/Contents/MacOS/"

# Check the architecture of the executable
echo "Checking executable architecture:"
file "$APP_BUNDLE/Contents/MacOS/$APP_NAME"
lipo -info "$APP_BUNDLE/Contents/MacOS/$APP_NAME" 2>/dev/null || echo "Not a universal binary"

# Create wrapper script to handle Tcl/Tk paths
echo "Creating Tcl/Tk wrapper..."
ORIGINAL_EXEC="$APP_BUNDLE/Contents/MacOS/${APP_NAME}_original"
WRAPPER_SCRIPT="$APP_BUNDLE/Contents/MacOS/$APP_NAME"

# Move original executable
mv "$WRAPPER_SCRIPT" "$ORIGINAL_EXEC"

# Create wrapper script
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
# QuickEDL macOS Tcl/Tk Wrapper

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_DIR="$( dirname "$( dirname "$SCRIPT_DIR" )" )"

# Set Tcl/Tk library paths
export TCL_LIBRARY="$APP_DIR/Contents/lib/tcl8.6"
export TK_LIBRARY="$APP_DIR/Contents/lib/tk8.6"

# Fallback paths
if [ ! -d "$TCL_LIBRARY" ]; then
    # Try to find Tcl/Tk in common locations
    for path in /opt/homebrew/lib/tcl8.6 /usr/local/lib/tcl8.6 /Library/Frameworks/Python.framework/Versions/*/lib/tcl8.6; do
        if [ -d "$path" ] && [ -f "$path/init.tcl" ]; then
            export TCL_LIBRARY="$path"
            break
        fi
    done
fi

if [ ! -d "$TK_LIBRARY" ]; then
    for path in /opt/homebrew/lib/tk8.6 /usr/local/lib/tk8.6 /Library/Frameworks/Python.framework/Versions/*/lib/tk8.6; do
        if [ -d "$path" ]; then
            export TK_LIBRARY="$path"
            break
        fi
    done
fi

# Additional library paths
export DYLD_FALLBACK_LIBRARY_PATH="$DYLD_FALLBACK_LIBRARY_PATH:/opt/homebrew/lib:/usr/local/lib"

# Execute the original binary
exec "$SCRIPT_DIR/${APP_NAME}_original" "$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Create Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIconFile</key>
    <string>icon_mac</string>
    <key>CFBundleIdentifier</key>
    <string>com.punkerschaf.quickedl</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleVersion</key>
    <string>${BUNDLE_VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

# Copy icon if it exists
if [ -f "resources/icon_mac.icns" ]; then
    cp "resources/icon_mac.icns" "$APP_BUNDLE/Contents/Resources/"
fi

# Make executable
chmod +x "$APP_BUNDLE/Contents/MacOS/${APP_NAME}"

# Ad-hoc code signing (removes quarantine issues)
echo "Signing the app bundle..."
codesign --force --deep --sign - "$APP_BUNDLE" 2>/dev/null || echo "Warning: Code signing failed, but app should still work"

# Remove extended attributes that might cause issues
xattr -cr "$APP_BUNDLE" 2>/dev/null || echo "Warning: Could not remove extended attributes"

echo "Created ${APP_BUNDLE}"
