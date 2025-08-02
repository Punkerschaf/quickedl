#!/bin/bash
# QuickEDL macOS Schnell-Reparatur
# Behebt die häufigsten "App ist beschädigt" Probleme

APP_PATH="/Applications/QuickEDL.app"

echo "🔧 QuickEDL macOS Schnell-Reparatur"
echo "=================================="

if [ ! -d "$APP_PATH" ]; then
    echo "❌ QuickEDL.app nicht in /Applications/ gefunden"
    exit 1
fi

echo "Repariere QuickEDL.app..."

# 1. Alle Extended Attributes entfernen
echo "• Entferne Extended Attributes..."
sudo xattr -cr "$APP_PATH" 2>/dev/null

# 2. Quarantäne spezifisch entfernen
echo "• Entferne Quarantäne..."
sudo xattr -d com.apple.quarantine "$APP_PATH" 2>/dev/null || true

# 3. Weitere problematische Attribute entfernen
echo "• Entferne weitere Attribute..."
sudo xattr -d com.apple.metadata:_kMDItemUserTags "$APP_PATH" 2>/dev/null || true
sudo xattr -d com.apple.FinderInfo "$APP_PATH" 2>/dev/null || true

# 4. Neue Code-Signierung erzwingen
echo "• Erstelle neue Code-Signierung..."
sudo codesign --force --deep --sign - "$APP_PATH" 2>/dev/null

# 5. Gatekeeper-Ausnahme hinzufügen
echo "• Füge Gatekeeper-Ausnahme hinzu..."
sudo spctl --add "$APP_PATH" 2>/dev/null || true
sudo spctl --enable "$APP_PATH" 2>/dev/null || true

# 6. Berechtigungen reparieren
echo "• Repariere Berechtigungen..."
sudo chmod -R 755 "$APP_PATH" 2>/dev/null
sudo chmod +x "$APP_PATH/Contents/MacOS/QuickEDL" 2>/dev/null

echo
echo "✅ Reparatur abgeschlossen!"
echo
echo "Versuchen Sie jetzt, QuickEDL zu öffnen:"
echo "• Doppelklick auf QuickEDL.app im Programme-Ordner"
echo "• Oder: open /Applications/QuickEDL.app"
echo
echo "Falls es immer noch nicht funktioniert:"
echo "• Starten Sie den Mac neu"
echo "• Oder verwenden Sie: ./diagnose_macos.sh für detaillierte Diagnose"
