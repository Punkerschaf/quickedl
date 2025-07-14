"""
Settings Manager for QuickEDL
Provides universal functions for loading, saving, and managing settings.
"""
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class SettingsManager:
    """
    Manages application settings with YAML storage and backwards compatibility.
    """
    
    def __init__(self):
        self.settings_folder = self._get_settings_folder()
        self.settings_file = self.settings_folder / "settings.yaml"
        self._settings_cache = {}
        self._default_settings = self._get_default_settings()
        
    def _get_settings_folder(self) -> Path:
        """Returns the path of the settings folder in the user's home directory."""
        try:
            home_dir = Path.home()
            settings_folder = home_dir / "quickedl"
            return settings_folder
        except Exception as e:
            logging.warning(f"Could not determine settings folder path. ({e})")
            # Fallback to current directory
            return Path.cwd() / "quickedl_settings"
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Returns the default settings dictionary."""
        return {
            'log_level': 'DEBUG',
            'funny': False,
            'default_dir': None,
            'delete_key': False,
            'window_geometry': '400x700',
            'theme': 'darkly',
            'auto_save_interval': 300  # seconds
        }
    
    def create_settings_folder(self) -> bool:
        """
        Creates the settings folder if it doesn't exist.
        Returns True if created or already exists, False on error.
        """
        try:
            self.settings_folder.mkdir(parents=True, exist_ok=True)
            logging.info(f"Settings folder created/verified at: {self.settings_folder}")
            return True
        except Exception as e:
            logging.error(f"Failed to create settings folder: {e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Loads settings from YAML file with backwards compatibility.
        Returns merged settings (defaults + loaded values).
        """
        # Start with default settings
        settings = self._default_settings.copy()
        
        if not self.settings_file.exists():
            logging.info("Settings file doesn't exist, using defaults")
            self._settings_cache = settings
            return settings
        
        try:
            with self.settings_file.open('r', encoding='utf-8') as file:
                loaded_settings = yaml.safe_load(file) or {} # {} -> Avoid NoneType
                
            # Merge loaded settings with defaults (loaded values override defaults)
            settings.update(loaded_settings)
            
            logging.info(f"Settings loaded from {self.settings_file}")
            logging.debug(f"Loaded settings: {loaded_settings}")
            
        except Exception as e:
            logging.error(f"Error loading settings file: {e}")
            logging.info("Using default settings")
        
        self._settings_cache = settings
        return settings
    
    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Saves settings to YAML file.
        Args:
            settings: Settings dictionary to save. If None, saves cached settings.
        Returns:
            True if successful, False otherwise.
        """
        if settings is None:
            settings = self._settings_cache
        
        if not self.settings_folder.exists():
            if not self.create_settings_folder():
                return False
        
        try:
            with self.settings_file.open('w', encoding='utf-8') as file:
                yaml.dump(settings, file, default_flow_style=False, allow_unicode=True)
            
            self._settings_cache = settings.copy()
            logging.info(f"Settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Gets a specific setting value.
        Args:
            key: Setting key (supports dot notation like 'ui.theme')
            default: Default value if key not found
        Returns:
            Setting value or default
        """
        try:
            # Support dot notation for nested settings
            value = self._settings_cache
            for part in key.split('.'):
                value = value[part]
            return value
        except (KeyError, TypeError):
            # For dot notation keys, just return the provided default
            if '.' in key:
                return default
            # For simple keys, try default_settings fallback
            return default if default is not None else self._default_settings.get(key)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Sets a specific setting value and saves to file.
        Args:
            key: Setting key (supports dot notation)
            value: New value
        Returns:
            True if successful, False otherwise
        """
        try:
            # Support dot notation for nested settings
            settings = self._settings_cache.copy()
            current = settings
            
            keys = key.split('.')
            for part in keys[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[keys[-1]] = value
            
            return self.save_settings(settings)
            
        except Exception as e:
            logging.error(f"Error setting '{key}' to '{value}': {e}")
            return False
    
    def update_settings(self, updates: Dict[str, Any]) -> bool:
        """
        Updates multiple settings at once.
        Args:
            updates: Dictionary of setting keys and values
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = self._settings_cache.copy()
            settings.update(updates)
            return self.save_settings(settings)
        except Exception as e:
            logging.error(f"Error updating settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Resets all settings to default values.
        Returns:
            True if successful, False otherwise
        """
        return self.save_settings(self._default_settings.copy())
    
    def get_settings_folder_path(self) -> Path:
        """Returns the settings folder path."""
        return self.settings_folder
    
    def get_settings_file_path(self) -> Path:
        """Returns the settings file path."""
        return self.settings_file
    
    def settings_folder_exists(self) -> bool:
        """Returns True if settings folder exists."""
        return self.settings_folder.exists()
    
    def settings_file_exists(self) -> bool:
        """Returns True if settings file exists."""
        return self.settings_file.exists()
    
    def get_auto_save_interval(self) -> int:
        """
        Gets the auto-save interval in seconds.
        Returns:
            Auto-save interval in seconds
        """
        return self.get_setting('auto_save_interval', 300)
