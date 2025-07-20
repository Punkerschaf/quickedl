#!/bin/bash
# Script to create macOS .app bundle from cx_Freeze output

BUILD_DIR="build"
APP_NAME="QuickEDL"
VERSION=$(python -c "from version import VERSION; print(VERSION)")

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "Error: Build directory not found. Run 'python setup_cxfreeze.py build' first."
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

echo "Created ${APP_BUNDLE}"
