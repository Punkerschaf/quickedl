"""
Settings Window for QuickEDL
Provides the UI for managing application settings.
"""
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from tkinter import BooleanVar, StringVar, filedialog
from pathlib import Path
import logging
import sys
import os

# Add parent directory to path for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import open_directory


class SettingsWindow:
    """
    Settings window for QuickEDL application.
    """
    
    def __init__(self, parent, settings_manager, app=None):
        self.parent = parent
        self.settings_manager = settings_manager
        self.app = app  # Reference to the main app for theme changes
        self.window = None
        self.settings_vars = {}
        
    def show(self):
        """Shows the settings window."""
        if self.window is not None:
            self.window.lift()
            self.window.focus_force()
            return
            
        self.window = ttk.Toplevel(self.parent)
        self.window.title("QuickEDL: Settings")
        self.window.geometry("500x800")
        self.window.resizable(True, True)
        
        # Load current settings
        current_settings = self.settings_manager.load_settings()
        
        # Bind close events only
        self.window.bind("<Escape>", self._close_window)
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)
        
        self._create_widgets(current_settings)
        
        # Center window and make it transient (but not modal)
        self.window.transient(self.parent)
        self._center_window()
        
        # Set focus without grab_set() to avoid input delays
        self.window.focus_force()
        
    def _create_widgets(self, settings):
        """Creates all widgets for the settings window."""
        
        # Main container with scrollable frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Settings folder section
        self._create_folder_section(main_frame, settings)
        
        # General settings section
        self._create_general_section(main_frame, settings)
        
        # Logging section
        self._create_logging_section(main_frame, settings)
        
        # Shortcuts section  
        self._create_shortcuts_section(main_frame, settings)
        
        # File handling section
        self._create_file_section(main_frame, settings)
        
        # Buttons section
        self._create_buttons_section(main_frame)
        
    def _create_folder_section(self, parent, settings):
        """Creates the settings folder section."""
        folder_frame = ttk.LabelFrame(parent, text=" Settings Folder ", padding=10)
        folder_frame.pack(fill="x", pady=(0, 10))
        
        # Folder path display
        folder_path_label = ttk.Label(
            folder_frame, 
            text=str(self.settings_manager.get_settings_folder_path()),
            wraplength=400
        )
        folder_path_label.pack(anchor="w")
        
        # Settings file path display (for debugging)
        file_path_label = ttk.Label(
            folder_frame, 
            text=f"Settings file: {self.settings_manager.get_settings_file_path()}",
            wraplength=400,
            foreground="gray"
        )
        file_path_label.pack(anchor="w", pady=(2, 0))
        
        # Folder status
        if self.settings_manager.settings_folder_exists():
            status_text = "✓ Folder exists"
            status_style = "success"
        else:
            status_text = "✗ Folder missing"
            status_style = "warning"
            
        status_label = ttk.Label(folder_frame, text=status_text, bootstyle=status_style)
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(folder_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Create folder button
        if not self.settings_manager.settings_folder_exists():
            create_button = ttk.Button(
                buttons_frame,
                text="Create Settings Folder",
                command=self._create_settings_folder,
                bootstyle="success"
            )
            create_button.pack(side="left", padx=(0, 10))
        
        # Open folder button
        open_button = ttk.Button(
            buttons_frame,
            text="Open Folder",
            command=self._open_settings_folder
        )
        open_button.pack(side="left")
        
    def _create_general_section(self, parent, settings):
        """Creates the general settings section."""
        general_frame = ttk.LabelFrame(parent, text=" General Settings ", padding=10)
        general_frame.pack(fill="x", pady=(0, 10))
        
        # Theme selection
        theme_frame = ttk.Frame(general_frame)
        theme_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(theme_frame, text="Theme:").pack(side="left")
        
        self.settings_vars['theme'] = StringVar(value=settings.get('theme', 'darkly'))
        self._theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.settings_vars['theme'],
            values=['darkly', 'litera'],
            state="readonly",
            width=15
        )
        self._theme_combo.pack(side="right")
        
        # Default directory
        dir_frame = ttk.Frame(general_frame)
        dir_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(dir_frame, text="Default directory:").pack(anchor="w")
        
        dir_display_frame = ttk.Frame(dir_frame)
        dir_display_frame.pack(fill="x", pady=(5, 0))
        
        self.settings_vars['default_dir'] = StringVar(value=settings.get('default_dir', '') or '')
        dir_entry = ttk.Entry(
            dir_display_frame,
            textvariable=self.settings_vars['default_dir'],
            state="readonly"
        )
        dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self._browse_button = ttk.Button(
            dir_display_frame,
            text="Browse",
            command=self._browse_default_directory,
            width=10
        )
        self._browse_button.pack(side="right")
        
    def _create_logging_section(self, parent, settings):
        """Creates the logging settings section."""
        logging_frame = ttk.LabelFrame(parent, text=" Logging ", padding=10)
        logging_frame.pack(fill="x", pady=(0, 10))
        
        # Log level
        level_frame = ttk.Frame(logging_frame)
        level_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(level_frame, text="Log level:").pack(side="left")
        
        self.settings_vars['log_level'] = StringVar(value=settings.get('log_level', 'DEBUG'))
        self._level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.settings_vars['log_level'],
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            state="readonly",
            width=15
        )
        self._level_combo.pack(side="right")
        
        # Log file button
        self._log_button = ttk.Button(
            logging_frame,
            text="Open Log File",
            command=self._open_log_file
        )
        self._log_button.pack(anchor="w")
        
    def _create_shortcuts_section(self, parent, settings):
        """Creates the shortcuts settings section."""
        shortcuts_frame = ttk.LabelFrame(parent, text=" Shortcuts ", padding=10)
        shortcuts_frame.pack(fill="x", pady=(0, 10))
        
        # Delete key shortcut
        self.settings_vars['delete_key'] = BooleanVar(value=settings.get('delete_key', False))
        self._delete_toggle = ttk.Checkbutton(
            shortcuts_frame,
            text="Delete last marker with backspace key",
            variable=self.settings_vars['delete_key'],
            bootstyle="success-round-toggle"
        )
        self._delete_toggle.pack(anchor="w")
        
    def _create_file_section(self, parent, settings):
        """Creates the file handling settings section."""
        file_frame = ttk.LabelFrame(parent, text=" File Handling ", padding=10)
        file_frame.pack(fill="x", pady=(0, 10))
        
        # Max recent files
        recent_frame = ttk.Frame(file_frame)
        recent_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(recent_frame, text="Max recent files:").pack(side="left")
        
        self.settings_vars['max_recent_files'] = StringVar(value=str(settings.get('max_recent_files', 10)))
        self._recent_spin = ttk.Spinbox(
            recent_frame,
            textvariable=self.settings_vars['max_recent_files'],
            from_=1,
            to=20,
            width=10
        )
        self._recent_spin.pack(side="right")
        
    def _create_buttons_section(self, parent):
        """Creates the buttons section."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Reset button
        self._reset_button = ttk.Button(
            buttons_frame,
            text="Reset to Defaults",
            command=self._reset_settings,
            bootstyle="warning-outline"
        )
        self._reset_button.pack(side="left")
        
        # Cancel button
        self._cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._close_window,
            bootstyle="secondary"
        )
        self._cancel_button.pack(side="right", padx=(10, 0))
        
        # Save button
        self._save_button = ttk.Button(
            buttons_frame,
            text="Save Settings",
            command=self._save_settings,
            bootstyle="success"
        )
        self._save_button.pack(side="right")
        
    def _create_settings_folder(self):
        """Creates the settings folder."""
        # Try to get current markerlabels from the app if available
        current_markerlabels = None
        if hasattr(self, 'app') and self.app and hasattr(self.app, 'markerlabel_entries'):
            current_markerlabels = [entry.get() for entry in self.app.markerlabel_entries]
            while len(current_markerlabels) < 9:
                current_markerlabels.append("")
        
        if self.settings_manager.create_settings_folder(current_markerlabels):
            Messagebox.show_info("Settings folder created successfully!")
            self._close_window()
            self.show()  # Refresh window
        else:
            Messagebox.show_error("Failed to create settings folder.")
            
    def _open_settings_folder(self):
        """Opens the settings folder in file manager."""
        folder_path = self.settings_manager.get_settings_folder_path()
        if folder_path.exists():
            open_directory(folder_path)
        else:
            Messagebox.show_error("Settings folder doesn't exist.")
            
    def _open_log_file(self):
        """Opens the log file."""
        log_file = Path.home() / "quickedl.log"
        if log_file.exists():
            open_directory(log_file)
        else:
            Messagebox.show_error("Log file not found.")
            
    def _browse_default_directory(self):
        """Opens directory browser for default directory."""
        directory = filedialog.askdirectory(
            title="Select Default Directory",
            initialdir=self.settings_vars['default_dir'].get() or Path.home()
        )
        if directory:
            self.settings_vars['default_dir'].set(directory)
            
    def _save_settings(self):
        """Saves all settings."""
        try:
            # Collect all settings from UI
            new_settings = {}
            
            for key, var in self.settings_vars.items():
                if isinstance(var, BooleanVar):
                    new_settings[key] = var.get()
                elif isinstance(var, StringVar):
                    value = var.get()
                    # Convert numeric strings to integers
                    if key in ['max_recent_files']:
                        try:
                            value = int(value)
                        except ValueError:
                            value = 10
                    # Handle empty default_dir
                    elif key == 'default_dir' and not value:
                        value = None
                    new_settings[key] = value
            
            # Save settings
            if self.settings_manager.update_settings(new_settings):
                # Apply theme immediately if changed
                if 'theme' in new_settings and self.app:
                    new_theme = new_settings['theme']
                    
                    try:
                        # Use the existing root window's style to change theme
                        self.app.root.style.theme_use(new_theme)
                        logging.info(f"Theme changed to: {new_theme}")
                    except Exception as e:
                        logging.error(f"Failed to apply theme '{new_theme}': {e}")
                
                # Apply log level immediately
                if 'log_level' in new_settings:
                    self._apply_log_level(new_settings['log_level'])
                    
                Messagebox.show_info("Settings saved successfully!")
                self._close_window()
            else:
                Messagebox.show_error("Failed to save settings.")

        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            Messagebox.show_error(f"Error saving settings: {e}")
            
    def _apply_log_level(self, level):
        """Applies the log level immediately."""
        try:
            logging.getLogger().setLevel(level)
            logging.info(f"Log level changed to {level}")
        except Exception as e:
            logging.error(f"Failed to set log level: {e}")
            
    def _reset_settings(self):
        """Resets settings to defaults."""
        result = Messagebox.show_question(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\nThis cannot be undone.",
            "Yes",
            "No"
        )
        
        if result == "Yes":
            if self.settings_manager.reset_to_defaults():
                Messagebox.show_info("Settings reset to defaults!")
                self._close_window()
            else:
                Messagebox.show_error("Failed to reset settings.")
                
    def _close_window(self, event=None):
        """Closes the settings window."""
        if self.window:
            self.window.destroy()
            self.window = None
            
    def _center_window(self):
        """Centers the window on the parent window."""
        self.window.update_idletasks()
        
        # Get window dimensions
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        
        # Get parent position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
