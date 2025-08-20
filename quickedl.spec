# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for QuickEDL
Supports Windows and macOS builds with proper app bundles
"""

import sys
import os
from pathlib import Path

# Get version
sys.path.insert(0, '.')
from version import VERSION

block_cipher = None

# Common data files and resources
datas = [
    ('resources', 'resources'),
]

# Hidden imports for ttkbootstrap and other dependencies
hiddenimports = [
    'ttkbootstrap',
    'yaml',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
]

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific configurations
if sys.platform == 'win32':
    # Windows executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='quickedl',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # Hide console window
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='resources/icon_win.ico',
        version_file=None,
    )

elif sys.platform == 'darwin':
    # macOS app bundle
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='quickedl',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='resources/icon_mac.icns',
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='quickedl',
    )
    
    app = BUNDLE(
        coll,
        name='QuickEDL.app',
        icon='resources/icon_mac.icns',
        bundle_identifier='com.punkerschaf.quickedl',
        version=VERSION,
        info_plist={
            'CFBundleDisplayName': 'QuickEDL',
            'CFBundleName': 'QuickEDL',
            'CFBundleVersion': VERSION,
            'CFBundleShortVersionString': VERSION,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSApplicationCategoryType': 'public.app-category.productivity',
            'NSHumanReadableCopyright': 'Copyright © 2024-2025 Eric Kirchheim',
            'LSMinimumSystemVersion': '10.14',
            'NSAppleEventsUsageDescription': 'QuickEDL needs access to create and manage EDL files.',
            'NSDocumentsFolderUsageDescription': 'QuickEDL needs access to your documents to save EDL files and project data.',
            'NSDesktopFolderUsageDescription': 'QuickEDL may need access to your desktop to save EDL files.',
            'NSDownloadsFolderUsageDescription': 'QuickEDL may need access to your downloads folder to save EDL files.',
        },
    )

else:
    # Linux/Unix - simple executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='quickedl',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='resources/icon_unix.png',
    )
