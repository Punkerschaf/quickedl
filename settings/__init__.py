"""
Settings package for QuickEDL
Provides settings management and UI components.
"""

from .settings_manager import SettingsManager
from .settings_window import SettingsWindow

# Convenience functions for backwards compatibility
def get_settings_folder():
    """Returns the settings folder path."""
    manager = SettingsManager()
    return manager.get_settings_folder_path()

def load_yaml(app):
    """Legacy function for loading settings into app object."""
    manager = SettingsManager()
    settings = manager.load_settings()
    
    # Apply settings to app object (backwards compatibility)
    if hasattr(app, 'log_level'):
        app.log_level = settings.get('log_level', app.log_level)
        set_log_level(app.log_level)
    
    if hasattr(app, 'funny'):
        app.funny = settings.get('funny', app.funny)
        
    if hasattr(app, 'default_dir'):
        app.default_dir = settings.get('default_dir', app.default_dir)
        
    if hasattr(app, 'delete_key'):
        app.delete_key = settings.get('delete_key', app.delete_key)

def set_log_level(level):
    """Sets the logging level."""
    import logging
    logging.getLogger().setLevel(level)
    logging.info(f"Logging level set to {level}")

def show_settings_window(app):
    """Shows the settings window."""
    if not hasattr(app, '_settings_manager'):
        app._settings_manager = SettingsManager()
    
    if not hasattr(app, '_settings_window'):
        app._settings_window = SettingsWindow(app.root, app._settings_manager)
    
    app._settings_window.show()

__all__ = ['SettingsManager', 'SettingsWindow', 'get_settings_folder', 'load_yaml', 'set_log_level', 'show_settings_window']
