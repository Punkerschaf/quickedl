# QuickEDL Build System (PyInstaller)

Dieses Build-System verwendet PyInstaller für Cross-Platform Builds von QuickEDL.

## Features

✅ **Separate Builds für alle Architekturen**:
- Windows x64 (.exe in .zip)
- macOS Intel x86_64 (.app in .dmg)
- macOS Apple Silicon arm64 (.app in .dmg)

✅ **Richtige macOS App-Bundles**:
- Vollständige `QuickEDL.app` mit Info.plist
- Native Berechtigungen für Dateizugriff
- Korrekte Icons und Metadaten

✅ **Automatische Paketierung**:
- Windows: .exe in .zip verpackt
- macOS: .app in .dmg verpackt

✅ **Flexible Builds**:
- Lokale Builds (nur aktuelle Architektur)
- GitHub Workflow (alle Architekturen)

## Lokale Builds

### Voraussetzungen
```bash
pip install pyinstaller
pip install -r dependencies.txt
```

### Build ausführen
```bash
python build.py
```

Das erstellt automatisch:
- **Windows**: `dist/quickedl_{VERSION}_winx64.zip`
- **macOS Intel**: `dist/quickedl_{VERSION}_macOS_x86_64.dmg`
- **macOS ARM64**: `dist/quickedl_{VERSION}_macOS_arm64.dmg`

### Build-Verifikation

Das Build-Skript überprüft automatisch:
- ✅ Executable wurde erstellt
- ✅ Architektur ist korrekt (macOS)
- ✅ App-Bundle-Struktur (macOS)
- ✅ Info.plist vorhanden (macOS)

## GitHub Actions Workflow

### Auslösung
Der Workflow wird **nur manuell** ausgelöst:
1. GitHub Repository → Actions Tab
2. "Build QuickEDL Executables" → "Run workflow"

### Build-Matrix
Der Workflow erstellt parallel:
- **Windows**: `windows-latest` Runner
- **macOS Intel**: `macos-13` Runner (Intel)
- **macOS Apple Silicon**: `macos-14` Runner (ARM64)

### Ausgabe
- **Artifacts**: Alle Builds werden als Artifacts gespeichert
- **Release**: Automatische Release-Erstellung mit allen Builds

## Dateistruktur

### Windows Build:
```
dist/
├── quickedl.exe                    # Hauptausführbare Datei
└── quickedl_{VERSION}_winx64.zip   # Gepackte Distribution
```

### macOS Build:
```
dist/
├── QuickEDL.app/                   # App Bundle
│   ├── Contents/
│   │   ├── Info.plist              # App-Metadaten
│   │   ├── MacOS/quickedl          # Ausführbare Datei
│   │   └── Resources/              # Icons und Ressourcen
└── quickedl_{VERSION}_macOS_{ARCH}.dmg  # Gepackte Distribution
```

## PyInstaller Konfiguration

Die `quickedl.spec` Datei enthält:

### Gemeinsame Konfiguration:
- **Hidden Imports**: ttkbootstrap, PIL, yaml, tkinter
- **Data Files**: resources/ Ordner mit Icons
- **Excludes**: Unnötige Pakete (matplotlib, numpy, etc.)

### Plattform-spezifische Konfiguration:

#### Windows:
- **Icon**: `resources/icon_win.ico`
- **Console**: Ausgeblendet (`console=False`)
- **Output**: Einzelne .exe Datei

#### macOS:
- **Icon**: `resources/icon_mac.icns`
- **Bundle**: Vollständige .app Struktur
- **Info.plist**: Berechtigungen und Metadaten
- **Bundle ID**: `com.punkerschaf.quickedl`

## Architektur-Handling

### Lokale Builds:
- Automatische Erkennung der aktuellen Architektur
- Umgebungsvariablen für architektur-spezifische Builds

### GitHub Actions:
- **Intel Runner** (`macos-13`): Explizit x86_64
- **ARM64 Runner** (`macos-14`): Explizit arm64
- Umgebungsvariablen setzen die Ziel-Architektur

## Troubleshooting

### Build schlägt fehl
```bash
# Überprüfe Dependencies
pip list | grep -E "(pyinstaller|ttkbootstrap|pyyaml|pillow)"

# Teste PyInstaller direkt
pyinstaller quickedl.spec --clean --noconfirm
```

### macOS: App startet nicht
```bash
# Überprüfe App-Bundle
file dist/QuickEDL.app/Contents/MacOS/quickedl
lipo -info dist/QuickEDL.app/Contents/MacOS/quickedl

# Überprüfe Info.plist
plutil -p dist/QuickEDL.app/Contents/Info.plist
```

### Windows: Missing DLLs
- PyInstaller sollte automatisch alle DLLs einbinden
- Bei Problemen: `--hidden-import` in der .spec hinzufügen

## Vergleich zu cx_Freeze

| Feature | PyInstaller | cx_Freeze |
|---------|-------------|-----------|
| macOS App Bundles | ✅ Vollständig | ⚠️ Kompliziert |
| Info.plist Integration | ✅ Native | ❌ Manuell |
| Cross-Platform | ✅ Excellent | ✅ Good |
| Architektur-Kontrolle | ✅ Einfach | ⚠️ Schwierig |
| Bundle-Größe | ✅ Optimiert | ✅ Optimiert |
| Konfiguration | ✅ .spec Datei | ❌ setup.py |
