# macOS Tcl/Tk Fix - Build Integration

Diese Änderungen lösen das "Can't find usable init.tcl" Problem direkt im Build-Prozess.

## Änderungen

### 1. GitHub Actions Workflows (`.github/workflows/build_cxfreeze.yml`)

**Intel Build (`macos-13`):**
```yaml
- name: Install system dependencies (macOS Intel)
  run: |
    brew install tcl-tk
    find /usr/local -name "init.tcl" 2>/dev/null || true
    python -c "import tkinter; print('Tkinter works')"
```

**Apple Silicon Build (`macos-14`):**
```yaml
- name: Install system dependencies (macOS Apple Silicon)
  run: |
    brew install tcl-tk
    find /opt/homebrew -name "init.tcl" 2>/dev/null || true
    python -c "import tkinter; print('Tkinter works')"
```

### 2. Setup.py Verbesserungen

**Verbesserte Tcl/Tk Erkennung:**
- Priorität: Homebrew → Python Framework → System
- Architektur-spezifische Pfade
- Validation mit `init.tcl` check

**Build-Options:**
```python
"environment": {
    "TCL_LIBRARY": "",  # Set by wrapper
    "TK_LIBRARY": "",   # Set by wrapper
}
```

### 3. App-Bundle Wrapper (`create_macos_app.sh`)

**Automatischer Wrapper:**
- Originale Executable → `QuickEDL_original`
- Neuer Wrapper → `QuickEDL` (bash script)
- Setzt `TCL_LIBRARY` und `TK_LIBRARY` Umgebungsvariablen
- Fallback-Suche für Tcl/Tk Pfade

### 4. Dependencies Update

**cx_Freeze Version:**
```
cx_Freeze>=6.15.0
```

## Erwartetes Verhalten

### Vor dem Fix:
```
_tkinter.TclError: Can't find usable init.tcl
```

### Nach dem Fix:
1. ✅ Homebrew installiert Tcl/Tk in GitHub Actions
2. ✅ setup.py findet und inkludiert Tcl/Tk-Bibliotheken
3. ✅ App-Bundle Wrapper setzt korrekte Umgebungsvariablen
4. ✅ App startet ohne Tcl/Tk-Fehler

## Debugging

**Build-Debug-Ausgabe zeigt:**
```bash
Found Tcl: /opt/homebrew/lib/tcl8.6
Found Tk: /opt/homebrew/lib/tk8.6
Tcl/Tk libraries check:
drwxr-xr-x tcl8.6
drwxr-xr-x tk8.6
Found: dist/QuickEDL.app/Contents/lib/tcl8.6/init.tcl
```

## No More Fix Scripts Needed

Mit diesen Änderungen entfallen:
- ❌ `fix_tcl_tk.sh`
- ❌ `fix_macos_app.sh` (für Tcl/Tk Probleme)
- ❌ Manuelle Benutzer-Interventionen

Die Apps sollten direkt nach der Installation funktionieren.
