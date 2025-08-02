#!/bin/bash
# QuickEDL macOS Diagnose-Skript
# Führt automatische Diagnose von macOS App-Problemen durch

APP_PATH="/Applications/QuickEDL.app"
EXECUTABLE_PATH="$APP_PATH/Contents/MacOS/QuickEDL"

echo "=== QuickEDL macOS Diagnose ==="
echo "Datum: $(date)"
echo "macOS Version: $(sw_vers -productVersion)"
echo "Architektur: $(uname -m)"
echo

# 1. App-Existenz prüfen
echo "1. App-Existenz prüfen..."
if [ -d "$APP_PATH" ]; then
    echo "✅ QuickEDL.app gefunden in /Applications/"
else
    echo "❌ QuickEDL.app nicht in /Applications/ gefunden"
    echo "   Bitte installieren Sie die App zuerst"
    exit 1
fi

# 2. Executable prüfen
echo
echo "2. Executable prüfen..."
if [ -f "$EXECUTABLE_PATH" ]; then
    echo "✅ Executable gefunden"
    echo "   Berechtigungen: $(ls -la "$EXECUTABLE_PATH" | awk '{print $1, $3, $4}')"
    
    if [ -x "$EXECUTABLE_PATH" ]; then
        echo "✅ Executable ist ausführbar"
    else
        echo "❌ Executable ist nicht ausführbar"
        echo "   Lösung: chmod +x '$EXECUTABLE_PATH'"
    fi
else
    echo "❌ Executable nicht gefunden"
    exit 1
fi

# 3. Architektur prüfen
echo
echo "3. Architektur prüfen..."
file_output=$(file "$EXECUTABLE_PATH")
echo "   Architektur: $file_output"

if echo "$file_output" | grep -q "arm64"; then
    echo "✅ ARM64 (Apple Silicon) unterstützt"
fi

if echo "$file_output" | grep -q "x86_64"; then
    echo "✅ x86_64 (Intel) unterstützt"
fi

# 4. Extended Attributes prüfen
echo
echo "4. Extended Attributes prüfen..."
xattr_output=$(xattr -l "$APP_PATH" 2>/dev/null)
if [ -n "$xattr_output" ]; then
    echo "⚠️  Extended Attributes gefunden:"
    echo "$xattr_output" | sed 's/^/   /'
    echo "   Lösung: sudo xattr -cr '$APP_PATH'"
else
    echo "✅ Keine problematischen Extended Attributes"
fi

# 5. Quarantäne prüfen
echo
echo "5. Quarantäne prüfen..."
if xattr -l "$APP_PATH" | grep -q "com.apple.quarantine"; then
    echo "⚠️  App ist in Quarantäne"
    echo "   Lösung: sudo xattr -d com.apple.quarantine '$APP_PATH'"
else
    echo "✅ App ist nicht in Quarantäne"
fi

# 6. Code-Signierung prüfen
echo
echo "6. Code-Signierung prüfen..."
codesign_output=$(codesign -dv --verbose=4 "$APP_PATH" 2>&1)
if echo "$codesign_output" | grep -q "adhoc"; then
    echo "✅ Ad-hoc Signierung vorhanden"
elif echo "$codesign_output" | grep -q "Signature="; then
    echo "✅ Code-Signierung vorhanden"
    echo "   Details: $(echo "$codesign_output" | grep "Authority=")"
else
    echo "⚠️  Keine gültige Code-Signierung"
    echo "   Lösung: sudo codesign --force --deep --sign - '$APP_PATH'"
fi

# 7. Gatekeeper Status
echo
echo "7. Gatekeeper Status prüfen..."
spctl_output=$(sudo spctl --assess --verbose "$APP_PATH" 2>&1)
if echo "$spctl_output" | grep -q "accepted"; then
    echo "✅ Von Gatekeeper akzeptiert"
else
    echo "⚠️  Von Gatekeeper abgelehnt:"
    echo "$spctl_output" | sed 's/^/   /'
    echo "   Lösung: sudo spctl --add '$APP_PATH'"
fi

# 8. Abhängigkeiten prüfen
echo
echo "8. Abhängigkeiten prüfen..."
if command -v otool >/dev/null 2>&1; then
    echo "   Dynamische Bibliotheken:"
    otool -L "$EXECUTABLE_PATH" | head -10 | sed 's/^/   /'
    
    # Prüfen auf fehlende Bibliotheken
    missing_libs=$(otool -L "$EXECUTABLE_PATH" | grep -v "$EXECUTABLE_PATH" | grep -v "/usr/lib" | grep -v "/System" | awk '{print $1}')
    if [ -n "$missing_libs" ]; then
        echo "   Externe Bibliotheken gefunden:"
        echo "$missing_libs" | sed 's/^/   /'
    fi
else
    echo "   otool nicht verfügbar für Abhängigkeitsprüfung"
fi

# 9. Teststart
echo
echo "9. Teststart durchführen..."
echo "   Versuche App direkt zu starten (5 Sekunden Timeout)..."

# Starte App mit Timeout
timeout 5s "$EXECUTABLE_PATH" --version 2>/dev/null && echo "✅ App startet erfolgreich" || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "⚠️  App startet, aber --version Flag wird nicht unterstützt"
    else
        echo "❌ App startet nicht (Exit Code: $exit_code)"
        echo "   Führen Sie aus: '$EXECUTABLE_PATH' für detaillierte Fehlermeldungen"
    fi
}

# 10. Crash Reports prüfen
echo
echo "10. Crash Reports prüfen..."
crash_reports=$(ls ~/Library/Logs/DiagnosticReports/QuickEDL* 2>/dev/null | head -5)
if [ -n "$crash_reports" ]; then
    echo "⚠️  Crash Reports gefunden:"
    echo "$crash_reports" | sed 's/^/   /'
    echo "   Neuester Report: $(ls -t ~/Library/Logs/DiagnosticReports/QuickEDL* 2>/dev/null | head -1)"
else
    echo "✅ Keine Crash Reports gefunden"
fi

echo
echo "=== Diagnose abgeschlossen ==="
echo
echo "Falls die App immer noch nicht funktioniert:"
echo "1. Führen Sie aus: '$EXECUTABLE_PATH'"
echo "2. Prüfen Sie Console.app auf QuickEDL-bezogene Meldungen"
echo "3. Kontaktieren Sie den Support mit dieser Diagnose-Ausgabe"
