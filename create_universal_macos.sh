#!/bin/bash
# Script to create a Universal macOS .app bundle by combining Intel and Apple Silicon builds

APP_NAME="QuickEDL"
VERSION=$(python -c "from version import VERSION; print(VERSION)")

echo "Creating Universal macOS app bundle for $APP_NAME v$VERSION"

# Check if we have both architectures available
INTEL_BUILD="build/exe.macosx-*-x86_64-*/QuickEDL"
ARM_BUILD="build/exe.macosx-*-arm64-*/QuickEDL"

INTEL_EXE=$(find . -path "$INTEL_BUILD" 2>/dev/null | head -1)
ARM_EXE=$(find . -path "$ARM_BUILD" 2>/dev/null | head -1)

if [ -z "$INTEL_EXE" ] && [ -z "$ARM_EXE" ]; then
    echo "Error: No executables found. You need to build for at least one architecture first."
    echo "Run: python setup.py build"
    exit 1
fi

if [ -n "$INTEL_EXE" ] && [ -n "$ARM_EXE" ]; then
    echo "Found both Intel and ARM executables, creating Universal binary..."
    
    # Create Universal binary using lipo
    mkdir -p temp_universal
    lipo -create "$INTEL_EXE" "$ARM_EXE" -output "temp_universal/QuickEDL"
    
    # Use the Intel build as base (they should be identical except for the executable)
    INTEL_DIR=$(dirname "$INTEL_EXE")
    
    # Create .app bundle structure
    APP_BUNDLE="dist/${APP_NAME}.app"
    rm -rf "$APP_BUNDLE"
    mkdir -p "$APP_BUNDLE/Contents/MacOS"
    mkdir -p "$APP_BUNDLE/Contents/Resources"
    
    # Copy everything except the executable
    cp -r "$INTEL_DIR/"* "$APP_BUNDLE/Contents/MacOS/"
    
    # Replace with Universal binary
    cp "temp_universal/QuickEDL" "$APP_BUNDLE/Contents/MacOS/"
    
    # Clean up
    rm -rf temp_universal
    
    echo "Created Universal binary"
    lipo -info "$APP_BUNDLE/Contents/MacOS/QuickEDL"
    
elif [ -n "$INTEL_EXE" ]; then
    echo "Found only Intel executable, creating Intel-only app..."
    EXE_DIR=$(dirname "$INTEL_EXE")
    
    # Create .app bundle structure
    APP_BUNDLE="dist/${APP_NAME}.app"
    rm -rf "$APP_BUNDLE"
    mkdir -p "$APP_BUNDLE/Contents/MacOS"
    mkdir -p "$APP_BUNDLE/Contents/Resources"
    
    # Copy executable and resources
    cp -r "$EXE_DIR/"* "$APP_BUNDLE/Contents/MacOS/"
    
elif [ -n "$ARM_EXE" ]; then
    echo "Found only ARM executable, creating ARM-only app..."
    EXE_DIR=$(dirname "$ARM_EXE")
    
    # Create .app bundle structure
    APP_BUNDLE="dist/${APP_NAME}.app"
    rm -rf "$APP_BUNDLE"
    mkdir -p "$APP_BUNDLE/Contents/MacOS"
    mkdir -p "$APP_BUNDLE/Contents/Resources"
    
    # Copy executable and resources
    cp -r "$EXE_DIR/"* "$APP_BUNDLE/Contents/MacOS/"
fi

# Create Info.plist (same as original script)
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
    <string>${VERSION}</string>
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

# Check final architecture
echo "Final executable architecture:"
file "$APP_BUNDLE/Contents/MacOS/$APP_NAME"
lipo -info "$APP_BUNDLE/Contents/MacOS/$APP_NAME" 2>/dev/null || echo "Single architecture binary"

# Ad-hoc code signing (removes quarantine issues)
echo "Signing the app bundle..."
codesign --force --deep --sign - "$APP_BUNDLE" 2>/dev/null || echo "Warning: Code signing failed, but app should still work"

# Remove extended attributes that might cause issues
xattr -cr "$APP_BUNDLE" 2>/dev/null || echo "Warning: Could not remove extended attributes"

echo "Created ${APP_BUNDLE}"
