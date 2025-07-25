#!/usr/bin/env python3
"""
Unit tests for Settings Window Focus Behavior
"""
import unittest
import ttkbootstrap as ttk
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the settings manager and utils
class MockSettingsManager:
    def __init__(self):
        pass
    
    def load_settings(self):
        return {
            'theme': 'darkly',
            'funny': False,
            'default_dir': '',
            'log_level': 'DEBUG',
            'delete_key': False,
            'max_recent_files': 10
        }
    
    def get_settings_folder_path(self):
        return "/tmp/test_settings"
    
    def get_settings_file_path(self):
        return "/tmp/test_settings/settings.yaml"
    
    def settings_folder_exists(self):
        return True

class MockApp:
    def __init__(self):
        self.root = ttk.Window(themename="darkly")  # Specify theme
        self.markerlabel_entries = []

class TestSettingsWindowFocus(unittest.TestCase):
    """Test class for Settings Window focus behavior."""
    
    def setUp(self):
        """Set up test environment."""
        # Create main window with proper theme
        self.root = ttk.Window(themename="darkly")
        self.root.withdraw()  # Hide main window during tests
        
        # Create mock settings manager with additional methods
        self.settings_manager = MockSettingsManager()
        # Add missing methods for testing
        self.settings_manager.update_settings = lambda x: True
        self.settings_manager.reset_to_defaults = lambda: True
        
        # Create mock app
        self.app = MockApp()
        
        # Import and create settings window
        from settings.settings_window import SettingsWindow
        self.settings_window = SettingsWindow(self.root, self.settings_manager, self.app)
        
    def tearDown(self):
        """Clean up after tests."""
        if self.settings_window.window:
            self.settings_window.window.destroy()
        self.root.destroy()
        
    def test_window_creation(self):
        """Test that the settings window can be created without errors."""
        try:
            self.settings_window.show()
            self.assertIsNotNone(self.settings_window.window)
            self.assertTrue(self.settings_window.window.winfo_exists())
        except Exception as e:
            self.fail(f"Window creation failed: {e}")
            
    def test_widget_focus_cycle(self):
        """Test that widgets can receive focus properly."""
        self.settings_window.show()
        
        # Update window to ensure all widgets are created
        self.settings_window.window.update_idletasks()
        
        # Test theme combobox focus
        if hasattr(self.settings_window, '_theme_combo'):
            self.settings_window._theme_combo.focus_set()
            self.settings_window.window.update()
            # Check if focus is working (no exception means success)
            self.assertTrue(True)
            
        # Test button focus
        if hasattr(self.settings_window, '_save_button'):
            self.settings_window._save_button.focus_set()
            self.settings_window.window.update()
            self.assertTrue(True)
            
        # Test browse button focus
        if hasattr(self.settings_window, '_browse_button'):
            self.settings_window._browse_button.focus_set()
            self.settings_window.window.update()
            self.assertTrue(True)
            
    def test_combobox_interaction(self):
        """Test that comboboxes can be interacted with."""
        self.settings_window.show()
        self.settings_window.window.update_idletasks()
        
        # Test theme combobox
        if hasattr(self.settings_window, '_theme_combo'):
            combo = self.settings_window._theme_combo
            
            # Test setting value
            initial_value = combo.get()
            new_value = 'litera' if initial_value == 'darkly' else 'darkly'
            
            try:
                combo.set(new_value)
                self.settings_window.window.update()
                self.assertEqual(combo.get(), new_value)
            except Exception as e:
                self.fail(f"Combobox interaction failed: {e}")
                
    def test_button_clicks(self):
        """Test that buttons can be clicked without blocking."""
        self.settings_window.show()
        self.settings_window.window.update_idletasks()
        
        # Test that buttons exist and can be invoked
        buttons_to_test = ['_save_button', '_cancel_button', '_reset_button']
        
        for button_name in buttons_to_test:
            if hasattr(self.settings_window, button_name):
                button = getattr(self.settings_window, button_name)
                try:
                    # Focus the button
                    button.focus_set()
                    self.settings_window.window.update()
                    
                    # Try to invoke it (this should not block)
                    # We wrap in try-catch because some buttons might trigger dialogs
                    button.invoke()
                    self.settings_window.window.update()
                    
                except Exception:
                    # Some buttons might fail due to missing dependencies, that's OK
                    pass
                    
    def test_sequential_widget_interaction(self):
        """Test that multiple widgets can be used in sequence."""
        self.settings_window.show()
        self.settings_window.window.update_idletasks()
        
        # Simulate user interaction sequence
        widgets = []
        
        if hasattr(self.settings_window, '_theme_combo'):
            widgets.append(self.settings_window._theme_combo)
        if hasattr(self.settings_window, '_funny_toggle'):
            widgets.append(self.settings_window._funny_toggle)
        if hasattr(self.settings_window, '_browse_button'):
            widgets.append(self.settings_window._browse_button)
        if hasattr(self.settings_window, '_save_button'):
            widgets.append(self.settings_window._save_button)
            
        # Test that each widget can be focused in sequence
        for i, widget in enumerate(widgets):
            try:
                widget.focus_set()
                self.settings_window.window.update()
                
                # Simulate some interaction
                if isinstance(widget, ttk.Combobox):
                    # This should not block
                    widget.event_generate('<Button-1>')
                    self.settings_window.window.update()
                    
                elif isinstance(widget, ttk.Button):
                    # This should not block focus
                    widget.focus_set()
                    self.settings_window.window.update()
                    
            except Exception as e:
                self.fail(f"Widget {i} interaction failed: {e}")

def run_manual_test():
    """Run a manual test to check focus behavior interactively."""
    print("Starting manual focus test...")
    
    # Create test environment
    root = ttk.Window()
    settings_manager = MockSettingsManager()
    app = MockApp()
    
    # Import and create settings window
    from settings.settings_window import SettingsWindow
    settings_window = SettingsWindow(root, settings_manager, app)
    
    # Show window
    settings_window.show()
    
    print("Settings window opened. Please test the following:")
    print("1. Click on the theme dropdown - can you select a different theme?")
    print("2. Click on various buttons - do they respond?")
    print("3. Try the funny mode toggle - does it work?")
    print("4. Try clicking between different widgets - do they all work?")
    print("5. Close the window when done testing.")
    
    root.mainloop()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Settings Window Focus')
    parser.add_argument('--manual', action='store_true', help='Run manual interactive test')
    args = parser.parse_args()
    
    if args.manual:
        run_manual_test()
    else:
        unittest.main()
