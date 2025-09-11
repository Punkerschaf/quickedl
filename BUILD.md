# QuickEDL Build System (PyInstaller)

This build system uses PyInstaller for cross-platform builds of QuickEDL.

## Features

✅ **Separate builds for all architectures**:
- Windows x64 (.exe in .zip)
- macOS Intel x86_64 (.app in .dmg)
- macOS Apple Silicon arm64 (.app in .dmg)

✅ **Proper macOS app bundles**:
- Complete `QuickEDL.app` with Info.plist
- Native file access permissions
- Correct icons and metadata

✅ **Automatic packaging**:
- Windows: .exe packaged in .zip
- macOS: .app packaged in .dmg

✅ **Flexible builds**:
- Local builds (current architecture only)
- GitHub workflow (all architectures)

## Local Builds

### Prerequisites
```bash
pip install pyinstaller
pip install -r dependencies.txt
```

### Run build
```bash
python build.py
```

This automatically creates:
- **Windows**: `dist/quickedl_{VERSION}_winx64.zip`
- **macOS Intel**: `dist/quickedl_{VERSION}_macOS_x86_64.dmg`
- **macOS ARM64**: `dist/quickedl_{VERSION}_macOS_arm64.dmg`

### Build verification

The build script automatically checks:
- ✅ Executable was created
- ✅ Architecture is correct (macOS)
- ✅ App bundle structure (macOS)
- ✅ Info.plist present (macOS)

## GitHub Actions Workflow

### Triggering
The workflow is **only triggered manually**:
1. GitHub Repository → Actions Tab
2. "Build QuickEDL Executables" → "Run workflow"

### Build matrix
The workflow creates in parallel:
- **Windows**: `windows-latest` runner
- **macOS Intel**: `macos-13` runner (Intel)
- **macOS Apple Silicon**: `macos-14` runner (ARM64)

### Output
- **Artifacts**: All builds are stored as artifacts
- **Release**: Automatic release creation with all builds

## File Structure

### Windows Build:
```
dist/
├── quickedl.exe                    # Main executable file
└── quickedl_{VERSION}_winx64.zip   # Packaged distribution
```

### macOS Build:
```
dist/
├── QuickEDL.app/                   # App Bundle
│   ├── Contents/
│   │   ├── Info.plist              # App metadata
│   │   ├── MacOS/quickedl          # Executable file
│   │   └── Resources/              # Icons and resources
└── quickedl_{VERSION}_macOS_{ARCH}.dmg  # Packaged distribution
```

## PyInstaller Configuration

The `quickedl.spec` file contains:

### Common configuration:
- **Hidden Imports**: ttkbootstrap, PIL, yaml, tkinter
- **Data Files**: resources/ folder with icons
- **Excludes**: Unnecessary packages (matplotlib, numpy, etc.)

### Platform-specific configuration:

#### Windows:
- **Icon**: `resources/icon_win.ico`
- **Console**: Hidden (`console=False`)
- **Output**: Single .exe file

#### macOS:
- **Icon**: `resources/icon_mac.icns`
- **Bundle**: Complete .app structure
- **Info.plist**: Permissions and metadata
- **Bundle ID**: `com.punkerschaf.quickedl`

## Architecture Handling

### Local builds:
- Automatic detection of current architecture
- Environment variables for architecture-specific builds

### GitHub Actions:
- **Intel Runner** (`macos-13`): Explicitly x86_64
- **ARM64 Runner** (`macos-14`): Explicitly arm64
- Environment variables set target architecture

## Troubleshooting

### Build fails
```bash
# Check dependencies
pip list | grep -E "(pyinstaller|ttkbootstrap|pyyaml|pillow)"

# Test PyInstaller directly
pyinstaller quickedl.spec --clean --noconfirm
```

### macOS: App won't start
```bash
# Check app bundle
file dist/QuickEDL.app/Contents/MacOS/quickedl
lipo -info dist/QuickEDL.app/Contents/MacOS/quickedl

# Check Info.plist
plutil -p dist/QuickEDL.app/Contents/Info.plist
```

### Windows: Missing DLLs
- PyInstaller should automatically include all DLLs
- If issues occur: Add `--hidden-import` in the .spec file

## Comparison to cx_Freeze

| Feature | PyInstaller | cx_Freeze |
|---------|-------------|-----------|
| macOS App Bundles | ✅ Complete | ⚠️ Complicated |
| Info.plist Integration | ✅ Native | ❌ Manual |
| Cross-Platform | ✅ Excellent | ✅ Good |
| Architecture Control | ✅ Easy | ⚠️ Difficult |
| Bundle Size | ✅ Optimized | ✅ Optimized |
| Configuration | ✅ .spec file | ❌ setup.py |
