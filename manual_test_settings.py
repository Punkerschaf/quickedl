#!/usr/bin/env python3
"""
Manual Test für Settings Window Focus-Verhalten
Dieses Skript öffnet das Settings Window direkt zum manuellen Testen.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import ttkbootstrap as ttk
    from settings.settings_manager import SettingsManager
    from settings.settings_window import SettingsWindow
    
    class TestApp:
        """Mock App für Testing"""
        def __init__(self):
            self.root = ttk.Window(themename="darkly")
            self.root.title("QuickEDL - Settings Test")
            self.root.geometry("400x300")
            
            # Mock markerlabel entries
            self.markerlabel_entries = []
            
            # Create main frame
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Instructions
            instructions = ttk.Label(
                main_frame,
                text="Klicken Sie auf 'Settings öffnen' um das Settings Window zu testen.\n\n"
                     "🎯 WICHTIG: Testen Sie NORMALE KLICKS (nicht lange drücken!):\n"
                     "• Theme Dropdown - öffnet sofort bei normalem Klick?\n"
                     "• Buttons - reagieren auf normalen Klick?\n"
                     "• Toggles - wechseln bei normalem Klick?\n"
                     "• Log Level Dropdown - funktioniert normal?\n"
                     "• KEIN langes Drücken (500ms+) nötig?",
                wraplength=350,
                justify="left"
            )
            instructions.pack(pady=(0, 20))
            
            # Button to open settings
            self.settings_button = ttk.Button(
                main_frame,
                text="Settings öffnen",
                command=self.open_settings,
                bootstyle="primary"
            )
            self.settings_button.pack(pady=10)
            
            # Status label
            self.status_label = ttk.Label(
                main_frame,
                text="Bereit zum Testen",
                bootstyle="info"
            )
            self.status_label.pack(pady=10)
            
            # Create settings manager
            self.settings_manager = SettingsManager()
            self.settings_window = None
            
        def open_settings(self):
            """Öffnet das Settings Window"""
            try:
                if self.settings_window is None:
                    self.settings_window = SettingsWindow(self.root, self.settings_manager, self)
                
                self.settings_window.show()
                self.status_label.config(text="Settings Window geöffnet - teste NORMALE Klicks (nicht lange drücken)!")
                self.status_label.config(bootstyle="warning")
            except Exception as e:
                self.status_label.config(text=f"Fehler: {e}")
                print(f"Fehler beim Öffnen der Settings: {e}")
                
        def run(self):
            """Startet die Test-Anwendung"""
            self.root.mainloop()
    
    if __name__ == "__main__":
        print("Starte Settings Window Click-Response Test...")
        print("🎯 HAUPTPROBLEM: Widgets brauchten 500ms+ lange Klicks")
        print("🔧 LÖSUNG: grab_set() entfernt für normale Click-Response")
        print()
        print("WICHTIG: Testen Sie NORMALE, KURZE Klicks:")
        print("1. Theme Dropdown - öffnet sofort bei normalem Klick?")
        print("2. Verschiedene Buttons - reagieren auf normalen Klick?") 
        print("3. Funny Mode Toggle - wechselt bei normalem Klick?")
        print("4. Log Level Dropdown - funktioniert normal?")
        print("5. KEIN langes Drücken nötig?")
        print()
        
        app = TestApp()
        app.run()
        
except ImportError as e:
    print(f"Import Fehler: {e}")
    print("Stellen Sie sicher, dass alle Dependencies installiert sind:")
    print("pip install ttkbootstrap")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
    import traceback
    traceback.print_exc()
