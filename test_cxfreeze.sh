#!/bin/bash
# Local test script for cx_Freeze build

echo "Testing cx_Freeze build locally..."

# Check if cx_Freeze is installed
if ! python -c "import cx_Freeze" 2>/dev/null; then
    echo "Installing cx_Freeze..."
    pip install cx_Freeze
fi

# Run the build
echo "Building with cx_Freeze..."
./build_cxfreeze.sh

# Check if build was successful
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "dist/QuickEDL.app" ]; then
        echo "✅ macOS .app bundle created successfully!"
        echo "You can run it with: open dist/QuickEDL.app"
    else
        echo "❌ macOS build failed"
        exit 1
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    if [ -f "dist/QuickEDL.exe" ]; then
        echo "✅ Windows executable created successfully!"
        echo "You can run it with: dist/QuickEDL.exe"
    else
        echo "❌ Windows build failed"
        exit 1
    fi
else
    if [ -f "dist/QuickEDL" ]; then
        echo "✅ Linux executable created successfully!"
        echo "You can run it with: ./dist/QuickEDL"
    else
        echo "❌ Linux build failed"
        exit 1
    fi
fi
