# QuickEDL macOS Troubleshooting

Dieses Dokument hilft bei der Diagnose und Behebung von macOS-spezifischen Problemen mit QuickEDL.

## 🔍 Schnelle Diagnose

**Sofort-Reparatur** (für das häufigste Problem):
```bash
curl -O https://raw.githubusercontent.com/Punkerschaf/quickedl/main/fix_macos_app.sh
chmod +x fix_macos_app.sh
./fix_macos_app.sh
```

**Tcl/Tk Problem beheben** (falls "Can't find usable init.tcl" Fehler):
```bash
curl -O https://raw.githubusercontent.com/Punkerschaf/quickedl/main/fix_tcl_tk.sh
chmod +x fix_tcl_tk.sh
./fix_tcl_tk.sh
```

**Vollständige Diagnose** (falls Reparatur nicht hilft):
```bash
curl -O https://raw.githubusercontent.com/Punkerschaf/quickedl/main/diagnose_macos.sh
chmod +x diagnose_macos.sh
./diagnose_macos.sh
```

Das Skript prüft automatisch:
- ✅ App-Installation und -Berechtigungen
- ✅ Architektur-Kompatibilität  
- ✅ Code-Signierung und Gatekeeper-Status
- ✅ Extended Attributes und Quarantäne
- ✅ Abhängigkeiten und Crash-Reports

## 🚨 Häufige Probleme

### Problem: App lässt sich nicht öffnen (kein Fehler sichtbar)

**Ursache**: Systemprotokolle zeigen oft irrelevante Meldungen. Die eigentliche Ursache ist meist:
- Falsche Architektur (Intel vs. Apple Silicon)
- Quarantäne-Attribute
- Fehlende Code-Signierung

**Lösung**:
```bash
# 1. Quarantäne entfernen
sudo xattr -cr /Applications/QuickEDL.app

# 2. Ad-hoc Signierung hinzufügen
sudo codesign --force --deep --sign - /Applications/QuickEDL.app

# 3. App über Terminal starten für detaillierte Fehler
/Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

### Problem: "App ist beschädigt" trotz erfolgreichem Diagnose-Test

**Symptom**: Das Diagnose-Skript meldet, dass die App funktioniert, aber beim Doppelklick erscheint "QuickEDL ist beschädigt".

**Ursache**: Gatekeeper blockiert die App aufgrund fehlender Notarisierung, obwohl sie technisch funktionsfähig ist.

**Komplette Lösung** (alle Schritte nacheinander ausführen):

```bash
# 1. Vollständige Attribute-Bereinigung
sudo xattr -cr /Applications/QuickEDL.app

# 2. Gatekeeper-Quarantäne komplett entfernen
sudo xattr -d com.apple.quarantine /Applications/QuickEDL.app 2>/dev/null || true

# 3. Neue Ad-hoc Signierung erzwingen
sudo codesign --force --deep --sign - /Applications/QuickEDL.app

# 4. Gatekeeper für diese App deaktivieren
sudo spctl --add /Applications/QuickEDL.app

# 5. Zusätzliche macOS-spezifische Attribute entfernen
sudo xattr -d com.apple.metadata:_kMDItemUserTags /Applications/QuickEDL.app 2>/dev/null || true
sudo xattr -d com.apple.FinderInfo /Applications/QuickEDL.app 2>/dev/null || true

# 6. App-Bundle-Struktur reparieren
sudo chmod -R 755 /Applications/QuickEDL.app
sudo chmod +x /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

**Alternative Methode** (falls obiges nicht funktioniert):

```bash
# Gatekeeper temporär systemweit deaktivieren
sudo spctl --master-disable

# App starten (sollte jetzt funktionieren)
open /Applications/QuickEDL.app

# Gatekeeper wieder aktivieren (nach erfolgreichem Start)
sudo spctl --master-enable
```

**Permanente Lösung** (empfohlen):

```bash
# App zur Gatekeeper-Ausnahmeliste hinzufügen
sudo spctl --add /Applications/QuickEDL.app
sudo spctl --enable /Applications/QuickEDL.app
```

### Problem: "Can't find usable init.tcl" Fehler

**Symptom**: App zeigt Fehler über fehlende Tcl/Tk-Bibliotheken beim Start über Terminal.

**Ursache**: cx_Freeze hat die Tcl/Tk-Bibliotheken nicht korrekt eingebunden.

**Sofortlösung**:
```bash
# Automatischer Tcl/Tk Fix
curl -O https://raw.githubusercontent.com/Punkerschaf/quickedl/main/fix_tcl_tk.sh
chmod +x fix_tcl_tk.sh
./fix_tcl_tk.sh
```

**Manuelle Lösung**:
```bash
# 1. Tcl-Bibliothek finden
find /Library/Frameworks/Python.framework -name "init.tcl" 2>/dev/null

# 2. Umgebungsvariablen setzen und App starten
export TCL_LIBRARY="/Library/Frameworks/Python.framework/Versions/3.10/lib/tcl8.6"
export TK_LIBRARY="/Library/Frameworks/Python.framework/Versions/3.10/lib/tk8.6"
/Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

**Alternative: Python mit Tkinter installieren**:
```bash
# Mit Homebrew
brew install python-tk

# Oder Anaconda/Miniconda verwenden
conda install tk
```

**Diagnose**:
```bash
# Prüfen Sie auf Crash-Reports
ls ~/Library/Logs/DiagnosticReports/QuickEDL*

# Neuesten Crash-Report anzeigen
ls -t ~/Library/Logs/DiagnosticReports/QuickEDL* | head -1 | xargs cat
```

**Häufige Ursachen**:
- Fehlende Python-Abhängigkeiten
- Inkompatible Bibliotheken
- Berechtigungsprobleme

## 🏗️ Architektur-spezifische Probleme

### Intel Macs (x86_64)
- Verwenden Sie: `quickedl_v{version}_macOS_Intel.dmg`
- Sollte direkt funktionieren

### Apple Silicon Macs (M1/M2/M3)
- **Empfohlen**: `quickedl_v{version}_macOS_AppleSilicon.dmg` 
- **Alternative**: Intel-Version mit Rosetta 2

**Architektur prüfen**:
```bash
# Ihre Mac-Architektur
uname -m

# App-Architektur  
file /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

## 🛠️ Erweiterte Fehlerbehebung

### Console.app für Live-Debugging
1. Öffnen Sie **Console.app** (Programme → Dienstprogramme)
2. Wählen Sie Ihren Mac in der Seitenleiste
3. Starten Sie Live-Protokollierung
4. Versuchen Sie QuickEDL zu öffnen
5. Filtern Sie nach "QuickEDL" in den Logs

### Terminal-basierte Diagnose
```bash
# Gatekeeper-Status prüfen
sudo spctl --assess --verbose /Applications/QuickEDL.app

# Abhängigkeiten prüfen
otool -L /Applications/QuickEDL.app/Contents/MacOS/QuickEDL

# Berechtigungen reparieren
chmod +x /Applications/QuickEDL.app/Contents/MacOS/QuickEDL
```

### System Policy Logs
```bash
# Systemrichtlinien-Entscheidungen anzeigen
log show --predicate 'subsystem == "com.apple.security.syspolicy"' --info --last 1h | grep -i quickedl
```

## 📞 Support

Falls diese Schritte nicht helfen:

1. **Führen Sie das Diagnose-Skript aus** und senden Sie die Ausgabe
2. **Teilen Sie relevante Crash-Reports** mit
3. **Geben Sie Ihre macOS-Version und Mac-Modell an**

Kontakt: [GitHub Issues](https://github.com/Punkerschaf/quickedl/issues)

## 🔄 Neuinstallation

Als letzter Ausweg:
```bash
# Vollständige Entfernung
rm -rf /Applications/QuickEDL.app
rm -rf ~/Library/Logs/DiagnosticReports/QuickEDL*

# Cache leeren
sudo rm -rf /System/Library/Caches/com.apple.codesigning.requirements

# Neuinstallation
# Laden Sie die richtige DMG für Ihre Architektur herunter
```
