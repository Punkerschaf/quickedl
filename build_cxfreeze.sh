#!/bin/bash
# Build script for cx_Freeze

echo "Building QuickEDL with cx_Freeze..."

# Clean previous builds
rm -rf build dist

# Build with cx_Freeze
python setup.py build

# Platform-specific post-processing
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Creating macOS .app bundle..."
    ./create_macos_app.sh
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "Processing Windows executable..."
    mkdir -p dist
    find build -name "QuickEDL.exe" -exec cp {} dist/ \;
else
    echo "Processing Linux executable..."
    mkdir -p dist
    find build -name "QuickEDL" -exec cp {} dist/ \;
fi

echo "Build completed!"
