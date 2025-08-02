#!/bin/bash
# QuickEDL macOS Tcl/Tk Fix
# Behebt das "Can't find usable init.tcl" Problem

APP_PATH="/Applications/QuickEDL.app"
EXECUTABLE_PATH="$APP_PATH/Contents/MacOS/QuickEDL"

echo "🔧 QuickEDL Tcl/Tk Reparatur"
echo "============================"

if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "❌ QuickEDL.app nicht gefunden"
    exit 1
fi

echo "Suche nach Tcl/Tk Bibliotheken..."

# Finde Tcl/Tk Pfade
TCL_PATHS=(
    "/Library/Frameworks/Python.framework/Versions/3.10/lib/tcl8.6"
    "/Library/Frameworks/Python.framework/Versions/3.11/lib/tcl8.6"
    "/System/Library/Frameworks/Tcl.framework/Versions/8.6/Resources/Scripts"
    "/usr/local/lib/tcl8.6"
)

TK_PATHS=(
    "/Library/Frameworks/Python.framework/Versions/3.10/lib/tk8.6"
    "/Library/Frameworks/Python.framework/Versions/3.11/lib/tk8.6"
    "/System/Library/Frameworks/Tk.framework/Versions/8.6/Resources/Scripts"
    "/usr/local/lib/tk8.6"
)

TCL_FOUND=""
TK_FOUND=""

for path in "${TCL_PATHS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/init.tcl" ]; then
        echo "✅ Tcl gefunden: $path"
        TCL_FOUND="$path"
        break
    fi
done

for path in "${TK_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ Tk gefunden: $path"
        TK_FOUND="$path"
        break
    fi
done

if [ -z "$TCL_FOUND" ]; then
    echo "❌ Tcl-Bibliothek nicht gefunden"
    echo "Installieren Sie Python mit Tkinter-Unterstützung:"
    echo "brew install python-tk"
    exit 1
fi

# Erstelle Wrapper-Skript
WRAPPER_SCRIPT="$APP_PATH/Contents/MacOS/QuickEDL_wrapper"

echo "Erstelle Wrapper-Skript..."
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# QuickEDL Tcl/Tk Wrapper

# Setze Tcl/Tk Umgebungsvariablen
export TCL_LIBRARY="$TCL_FOUND"
export TK_LIBRARY="$TK_FOUND"
export TCLLIBPATH="$TCL_FOUND"

# Zusätzliche Pfade für die App
export DYLD_FALLBACK_LIBRARY_PATH="\$DYLD_FALLBACK_LIBRARY_PATH:/Library/Frameworks/Python.framework/Versions/3.10/lib:/Library/Frameworks/Python.framework/Versions/3.11/lib"

# Starte die eigentliche App
exec "\$( dirname "\$0" )/QuickEDL_original" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Verschiebe Original und erstelle neuen Wrapper
if [ ! -f "$APP_PATH/Contents/MacOS/QuickEDL_original" ]; then
    echo "Verschiebe Original-Executable..."
    mv "$EXECUTABLE_PATH" "$APP_PATH/Contents/MacOS/QuickEDL_original"
    mv "$WRAPPER_SCRIPT" "$EXECUTABLE_PATH"
fi

echo "✅ Tcl/Tk Fix installiert!"
echo
echo "Versuchen Sie jetzt, QuickEDL zu starten:"
echo "• Doppelklick auf QuickEDL.app"
echo "• Oder: open /Applications/QuickEDL.app"
