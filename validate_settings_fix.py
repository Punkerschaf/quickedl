#!/usr/bin/env python3
"""
Validierung der Settings Window Focus-Reparatur
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_settings_window_code():
    """Validiert den Settings Window Code auf problematische Event-Handler"""
    
    print("=== Settings Window Code Validierung ===\n")
    
    # Read the settings window file
    settings_file = "/Users/erickirchheim/Documents/GitHub/quickedl/settings/settings_window.py"
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for problematic patterns
        problems = []
        fixes = []
        
        # Check for removed problematic event handlers
        if '<Button-1>' in content and 'self.window.bind("<Button-1>"' in content:
            problems.append("❌ Window-level <Button-1> binding noch vorhanden")
        else:
            fixes.append("✅ Window-level <Button-1> binding entfernt")
            
        if '<FocusIn>' in content and 'self.window.bind("<FocusIn>"' in content:
            problems.append("❌ Window-level <FocusIn> binding noch vorhanden")
        else:
            fixes.append("✅ Window-level <FocusIn> binding entfernt")
            
        if '<<ComboboxSelected>>' in content:
            problems.append("❌ Custom Combobox Event-Handler noch vorhanden")
        else:
            fixes.append("✅ Custom Combobox Event-Handler entfernt")
            
        if '_setup_tab_order' in content:
            problems.append("❌ Custom Tab-Order System noch vorhanden")
        else:
            fixes.append("✅ Custom Tab-Order System entfernt")
            
        if '_on_combobox_selected' in content:
            problems.append("❌ _on_combobox_selected Methode noch vorhanden")
        else:
            fixes.append("✅ _on_combobox_selected Methode entfernt")
            
        if '_on_combobox_click' in content:
            problems.append("❌ _on_combobox_click Methode noch vorhanden")
        else:
            fixes.append("✅ _on_combobox_click Methode entfernt")
            
        if '_on_window_click' in content:
            problems.append("❌ _on_window_click Methode noch vorhanden")
        else:
            fixes.append("✅ _on_window_click Methode entfernt")
            
        if '_initial_focus' in content:
            problems.append("❌ _initial_focus Methode noch vorhanden")
        else:
            fixes.append("✅ _initial_focus Methode entfernt")
        
        # Check for essential functionality still present
        if 'grab_set()' not in content:
            problems.append("❌ Modal grab_set() fehlt")
        else:
            fixes.append("✅ Modal grab_set() vorhanden")
            
        if 'transient(' not in content:
            problems.append("❌ Window transient() fehlt")
        else:
            fixes.append("✅ Window transient() vorhanden")
            
        if '<Escape>' not in content:
            problems.append("❌ Escape-Key binding fehlt")
        else:
            fixes.append("✅ Escape-Key binding vorhanden")
        
        # Report results
        print("BEHOBENE PROBLEME:")
        for fix in fixes:
            print(f"  {fix}")
            
        if problems:
            print("\nVERBLEIBENDE PROBLEME:")
            for problem in problems:
                print(f"  {problem}")
            print("\n❌ Code-Validierung fehlgeschlagen!")
            return False
        else:
            print(f"\n✅ Code-Validierung erfolgreich! {len(fixes)} Verbesserungen implementiert.")
            return True
            
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Datei: {e}")
        return False

def print_usage_instructions():
    """Gibt Anweisungen für die Nutzung aus"""
    print("\n=== NUTZUNGSANWEISUNGEN ===")
    print()
    print("1. MANUELLER TEST:")
    print("   python manual_test_settings.py")
    print("   - Teste alle Widgets in Sequenz")
    print("   - Achte auf responsive Buttons und Dropdowns")
    print()
    print("2. ZU TESTENDE SZENARIEN:")
    print("   ✓ Theme Dropdown mehrmals ändern")
    print("   ✓ Nach Dropdown-Änderung andere Buttons klicken")
    print("   ✓ Zwischen verschiedenen Widgets wechseln")
    print("   ✓ Checkboxes und Spinboxes verwenden")
    print("   ✓ Settings speichern und zurücksetzen")
    print()
    print("3. ERWARTETES VERHALTEN:")
    print("   ✓ Alle Widgets reagieren prompt")
    print("   ✓ Keine blockierenden Interaktionen")
    print("   ✓ Standard Tab-Navigation funktioniert")
    print("   ✓ Focus wird nicht 'gefangen'")

if __name__ == "__main__":
    success = validate_settings_window_code()
    print_usage_instructions()
    
    if success:
        print("\n🎉 Settings Window wurde erfolgreich repariert!")
        print("Das Focus-Problem sollte jetzt behoben sein.")
    else:
        print("\n⚠️  Es gibt noch Probleme im Code, die behoben werden müssen.")
