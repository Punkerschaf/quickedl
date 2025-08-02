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

### Erweiterte Diagnose

**Automatische Diagnose** (empfohlen):
```bash
# Laden Sie das Diagnose-Skript herunter und führen Sie es aus
curl -O https://raw.githubusercontent.com/Punkerschaf/quickedl/main/diagnose_macos.sh
chmod +x diagnose_macos.sh
./diagnose_macos.sh
```

Falls die App sich immer noch nicht öffnen lässt, führen Sie diese **manuellen Schritte** zur Diagnose durch:

#### 1. App-Status prüfen
```bash
# Prüfen Sie die App-Berechtigungen
ls -la /Applications/QuickEDL.app/Contents/MacOS/QuickEDL

# Prüfen Sie Extended Attributes
xattr -l /Applications/QuickEDL.app

# Prüfen Sie Code-Signierung
codesign -dv --verbose=4 /Applications/QuickEDL.app
```

#### 2. Direkte Ausführung im Terminal
Versuchen Sie die App direkt vom Terminal aus zu starten, um spezifische Fehlermeldungen zu sehen:
```bash
# Direkte Ausführung
/Applications/QuickEDL.app/Contents/MacOS/QuickEDL

# Mit detaillierter Ausgabe
DYLD_PRINT_LIBRARIES=1 /Applications/QuickEDL.app/Contents/MacOS/QuickEDL

# Python-spezifische Debug-Ausgabe
PYTHONVERBOSE=1 /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

#### 3. Console.app verwenden
1. Öffnen Sie die **Console.app** (Programme → Dienstprogramme → Konsole)
2. Wählen Sie Ihren Mac in der Seitenleiste
3. Klicken Sie auf "Start" um Live-Protokollierung zu beginnen
4. Versuchen Sie QuickEDL zu starten
5. Suchen Sie nach Einträgen mit "QuickEDL" oder "QuickEDL"

#### 4. Crash-Reports prüfen
```bash
# Prüfen Sie auf Crash-Reports
ls ~/Library/Logs/DiagnosticReports/QuickEDL*
```

Falls Crash-Reports vorhanden sind, zeigen Sie den neuesten an:
```bash
# Zeigen Sie den neuesten Crash-Report
ls -t ~/Library/Logs/DiagnosticReports/QuickEDL* | head -1 | xargs cat
```

#### 5. Spade (System Policy) prüfen
```bash
# Prüfen Sie System Policy Entscheidungen
log show --predicate 'subsystem == "com.apple.security.syspolicy"' --info --last 1h | grep -i quickedl
```

#### 6. Gatekeeper Status
```bash
# Prüfen Sie Gatekeeper Status
sudo spctl --assess --verbose /Applications/QuickEDL.app

# Gatekeeper für diese App temporär deaktivieren
sudo spctl --add /Applications/QuickEDL.app
```

### Häufige Probleme und Lösungen

#### Problem: "QuickEDL kann nicht geöffnet werden, da es beschädigt ist"
**Lösung**:
```bash
sudo xattr -cr /Applications/QuickEDL.app
sudo codesign --force --deep --sign - /Applications/QuickEDL.app
```

#### Problem: "QuickEDL kann nicht geöffnet werden, da der Entwickler nicht überprüft werden kann"
**Lösung**:
1. Rechtsklick auf QuickEDL.app → "Öffnen"
2. Klicken Sie "Öffnen" im Sicherheitsdialog
3. Oder verwenden Sie:
```bash
sudo spctl --master-disable  # Temporär Gatekeeper deaktivieren
# Nach dem ersten Start:
sudo spctl --master-enable   # Gatekeeper wieder aktivieren
```

#### Problem: App startet aber stürzt sofort ab
**Lösung**:
1. Prüfen Sie Python-Abhängigkeiten:
```bash
/Applications/QuickEDL.app/Contents/MacOS/QuickEDL --version
```

2. Prüfen Sie auf fehlende Bibliotheken:
```bash
otool -L /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

#### Problem: "Keine Berechtigung" Fehler
**Lösung**:
```bash
chmod +x /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
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
