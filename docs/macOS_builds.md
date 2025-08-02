# macOS Build Guide

QuickEDL bietet verschiedene macOS Builds für unterschiedliche Architekturen:

## Verfügbare Builds

### 1. Intel (x86_64) Build
- **Datei**: `quickedl_v{version}_macOS_Intel.dmg`
- **Kompatibilität**: Intel-basierte Macs und Apple Silicon Macs mit Rosetta 2
- **Empfohlen für**: Ältere Intel-Macs

### 2. Apple Silicon (ARM64) Build  
- **Datei**: `quickedl_v{version}_macOS_AppleSilicon.dmg`
- **Kompatibilität**: Apple Silicon Macs (M1, M2, M3, etc.)
- **Empfohlen für**: Neuere Apple Silicon Macs für beste Performance

## Installation

1. Laden Sie die passende DMG-Datei für Ihre Mac-Architektur herunter
2. Öffnen Sie die DMG-Datei
3. Ziehen Sie QuickEDL.app in den Programme-Ordner
4. **Wichtig**: Beim ersten Start mit Rechtsklick → "Öffnen" starten, um Gatekeeper zu umgehen

## Fehlerbehebung

### "App ist beschädigt" Fehlermeldung

Falls Sie die Meldung "QuickEDL ist beschädigt" erhalten:

1. Öffnen Sie das Terminal
2. Führen Sie folgenden Befehl aus:
   ```bash
   sudo xattr -cr /Applications/QuickEDL.app
   ```
3. Versuchen Sie die App erneut zu starten

### Quarantäne entfernen

Alternative Lösung für Quarantäne-Probleme:
```bash
sudo xattr -d com.apple.quarantine /Applications/QuickEDL.app
```

### Architektur prüfen

Um zu prüfen, welche Architektur Sie haben:
```bash
uname -m
```
- `x86_64` = Intel Mac
- `arm64` = Apple Silicon Mac

Um die Architektur der App zu prüfen:
```bash
file /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

## Entwickler-Hinweise

### Lokales Erstellen

Für Intel Build:
```bash
# Auf Intel Mac oder mit Rosetta
python setup.py build
./create_macos_app.sh
```

Für Apple Silicon Build:
```bash
# Auf Apple Silicon Mac
python setup.py build  
./create_macos_app.sh
```

### Universal Binary (experimentell)

Um eine Universal Binary zu erstellen (funktioniert nur, wenn beide Architekturen verfügbar sind):
```bash
./create_universal_macos.sh
```

## Code-Signierung

Die bereitgestellten Apps sind mit ad-hoc Signierung versehen, um Quarantäne-Probleme zu minimieren. Für Entwickler mit einem Developer-Zertifikat:

```bash
codesign --force --deep --sign "Developer ID Application: Your Name" QuickEDL.app
```
