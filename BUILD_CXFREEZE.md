# cx_Freeze Build-System für QuickEDL

Dieses Verzeichnis enthält die Konfiguration für das neue cx_Freeze Build-System, das PyInstaller ersetzen soll.

## Dateien

- `setup.py` - Hauptkonfiguration für cx_Freeze
- `build_cxfreeze.sh` - Lokales Build-Skript
- `create_macos_app.sh` - Erstellt macOS .app Bundles
- `test_cxfreeze.sh` - Test-Skript für lokale Builds
- `.github/workflows/build_cxfreeze.yml` - GitHub Actions Workflow

## Lokaler Build

### Voraussetzungen
```bash
pip install cx_Freeze
pip install -r dependencies.txt
```

### Build durchführen
```bash
# Automatischer Build mit Test
./test_cxfreeze.sh

# Oder manuell
./build_cxfreeze.sh
```

## Unterstützte Plattformen

### Windows
- Erstellt `QuickEDL.exe`
- Package: `quickedl_v{VERSION}_Windows.zip`

### macOS
- Erstellt `QuickEDL.app` Bundle
- Architekturen: x86_64 und arm64
- Package: `quickedl_v{VERSION}_macOS{ARCH}.dmg`

### Linux
- Erstellt `QuickEDL` Binary
- Package: `quickedl_v{VERSION}_Linux.zip`

## GitHub Actions

Der neue Workflow erstellt automatisch:
- Windows: ZIP-Datei mit .exe
- macOS: DMG-Dateien für Intel und Apple Silicon
- Linux: ZIP-Datei mit Binary

Alle Dateien enthalten Version und Architektur im Dateinamen.

## Unterschiede zu PyInstaller

### Vorteile von cx_Freeze:
- Bessere Kontrolle über Bundle-Struktur
- Kleinere ausführbare Dateien
- Konsistentere Builds zwischen Plattformen
- Native macOS .app Bundle-Unterstützung

### Setup:
- Konfiguration in `setup.py` anstatt `.spec` Datei
- Modulare Build-Skripte
- Plattformspezifische Anpassungen

## Migration von PyInstaller

Der bestehende PyInstaller-Workflow bleibt vorerst erhalten:
- `pyinstaller.bash` - Lokales PyInstaller-Skript
- `quickedl.spec` - PyInstaller-Konfiguration  
- `.github/workflows/build_executables.yaml` - PyInstaller GitHub Actions

Dies ermöglicht einen schrittweisen Übergang und Vergleich der beiden Systeme.
