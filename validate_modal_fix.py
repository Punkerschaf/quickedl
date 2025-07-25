#!/usr/bin/env python3
"""
Validierung der Settings Window Modal-Fixes
Überprüft, ob grab_set() entfernt wurde, um Click-Delays zu beheben
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_modal_fixes():
    """Überprüft ob die Modal-Dialog-Probleme behoben wurden"""
    print("=== Settings Window Modal-Fix Validierung ===\n")
    
    settings_file = Path("settings/settings_window.py")
    
    if not settings_file.exists():
        print("❌ Settings window file nicht gefunden!")
        return False
        
    content = settings_file.read_text()
    
    fixes_applied = []
    issues_found = []
    
    # Check 1: grab_set() sollte entfernt sein (aber nicht in Kommentaren)
    import re
    grab_set_pattern = r'^\s*[^#]*\.grab_set\(\)'  # Nicht in Kommentaren
    if not re.search(grab_set_pattern, content, re.MULTILINE):
        fixes_applied.append("✅ grab_set() entfernt (behebt Click-Delays)")
    else:
        issues_found.append("❌ grab_set() noch vorhanden (verursacht Click-Delays)")
    
    # Check 2: grab_release() sollte entfernt sein (aber nicht in Kommentaren)
    grab_release_pattern = r'^\s*[^#]*\.grab_release\(\)'  # Nicht in Kommentaren
    if not re.search(grab_release_pattern, content, re.MULTILINE):
        fixes_applied.append("✅ grab_release() entfernt")
    else:
        issues_found.append("❌ grab_release() noch vorhanden")
        
    # Check 3: transient() sollte noch da sein
    if "transient(" in content:
        fixes_applied.append("✅ transient() beibehalten (Fenster-Hierarchie)")
    else:
        issues_found.append("❌ transient() fehlt")
        
    # Check 4: focus_force() sollte noch da sein
    if "focus_force()" in content:
        fixes_applied.append("✅ focus_force() beibehalten")
    else:
        issues_found.append("❌ focus_force() fehlt")
        
    # Check 5: Keine problematischen Event-Handler mehr
    problematic_bindings = [
        "<Button-1>", 
        "<FocusIn>",
        "<<ComboboxSelected>>",
        "_on_combobox_",
        "_on_window_",
        "_setup_tab_order"
    ]
    
    for binding in problematic_bindings:
        if binding not in content:
            fixes_applied.append(f"✅ {binding} entfernt")
        else:
            issues_found.append(f"❌ {binding} noch vorhanden")
    
    # Ergebnisse anzeigen
    if fixes_applied:
        print("ERFOLGREICH BEHOBENE PROBLEME:")
        for fix in fixes_applied:
            print(f"  {fix}")
        print()
        
    if issues_found:
        print("VERBLEIBENDE PROBLEME:")
        for issue in issues_found:
            print(f"  {issue}")
        print()
        return False
    else:
        print(f"✅ Modal-Fix Validierung erfolgreich! {len(fixes_applied)} Verbesserungen implementiert.\n")
        
        print("=== ERWARTETES VERHALTEN NACH FIX ===")
        print("✓ Normale Klicks (nicht lange drücken) funktionieren")
        print("✓ Dropdowns öffnen sich sofort bei Klick")
        print("✓ Buttons reagieren auf normale Klicks")
        print("✓ Toggles wechseln bei einfachem Klick")
        print("✓ Keine 500ms+ Click-Delays mehr")
        print()
        
        print("🎯 Das Settings Window ist jetzt NICHT mehr modal,")
        print("   aber alle Funktionen sollten normal reagieren!")
        return True

if __name__ == "__main__":
    success = validate_modal_fixes()
    if success:
        print("\n🎉 Modal-Fix erfolgreich! Testen Sie jetzt normale Klicks.")
    else:
        print("\n⚠️  Noch Probleme gefunden - weitere Fixes nötig.")
    
    sys.exit(0 if success else 1)
