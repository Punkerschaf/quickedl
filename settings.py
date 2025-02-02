import yaml
import logging
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa: F403
from tkinter import BooleanVar

from utils import open_directory

#######################
### SETTINGS FOLDER ###
#######################

def get_settings_folder():
    """Returns the path of the settings folder in the user'S home directory.
    Does NOT generating the folder if it don'T exist.
    Returns: Path object or None"""
    try:
        home_dir = Path.home()
        settings_folder = home_dir  / "quickedl"
        return settings_folder
    except Exception as e:
        print(f"Error: Could not find settings folder. ({e})")

def load_yaml(app):
    """Searchs for settings.yaml in the settings folder and loads them into the app.
    Returns: Nothing. Updates variables of the app object."""
    settings_file = app.settings_folder / "settings.yaml"
    if settings_file.exists():
        with settings_file.open('r') as file:
            settings_data = yaml.safe_load(file)

            # Log Level
            app.log_level = settings_data.get('log_level', app.log_level)
            set_log_level(app.log_level)

            # Funny mode
            app.funny = settings_data.get('funny', app.funny)

            # Default directory
            app.default_dir = settings_data.get('default_dir', app.default_dir)
    else:
        print("Error: Could not find settings file")
        return

def set_log_level(level):
        logging.getLogger().setLevel(level)
        logging.info(f"Logging level set to {level}")


#######################
### Settings WINDOW ###
#######################

def show_settings_window(app):
    """Shows the settings window of the app object."""
    settings_window = ttk.Toplevel(app.root)
    settings_window.title("QuickEDL: Settings")
    settings_window.geometry("400x350")

    def update_folder_indicator(app, folder_indicator):
        if app.settings_folder.exists():
            folder_indicator.config(text="found", bootstyle="success")
        else:
            return

    def close_settings_window(self, event = None):
        settings_window.destroy()
    
    def open_log_file(event = None):
        log_file = Path.home() / "quickedl.log"
        if log_file.exists():
            open_directory(log_file)

    settings_window.bind("<Escape>", close_settings_window)

# settings folder
    settings_folder_frame = ttk.LabelFrame(settings_window, text=" settings folder")
    settings_folder_frame.pack(padx= 10, pady=5, fill='x',)
    folder_label = ttk.Label(settings_folder_frame, textvariable=app.settings_folder_str, justify="left")
    folder_label.pack(padx=5)
    folder_indicator = ttk.Label(settings_folder_frame, text="not found", bootstyle="warning")
    folder_indicator.pack()
    update_folder_indicator(app, folder_indicator)

# Logging
    logging_frame = ttk.Labelframe(settings_window, text=" Logging ")
    logging_frame.pack(padx=10, pady=5, fill='x')
    log_level_label = ttk.Label(logging_frame, text=f"Log level: {app.log_level}")
    log_level_label.pack(pady=5)
    log_file_button = ttk.Button(logging_frame, text="show log file", command=open_log_file)
    log_file_button.pack(pady=5)

# default edl path
    default_edl_frame = ttk.LabelFrame(settings_window, text=" default directory ")
    default_edl_frame.pack(padx=10, pady=5, fill='x')
    default_path_label = ttk.Label(default_edl_frame, text=app.default_dir, bootstyle="warning")
    default_path_label.pack(pady=5)

# misc settings
    misc_frame = ttk.LabelFrame(settings_window, text=" misc ")
    misc_frame.pack(padx=10, pady=5, fill='x')
    funny_var = BooleanVar(value=app.funny)
    funny_toggle = ttk.Checkbutton(misc_frame, text="funny mode", bootstyle="success-square-toggle",
                                   variable=funny_var, command=lambda: setattr(app, 'funny', funny_var.get()))
    funny_toggle.pack(pady=5)

# close Button
    confirmation_frame = ttk.Frame(settings_window)
    confirmation_frame.pack(pady=5)
    close_button = ttk.Button(confirmation_frame, text="Close", command=settings_window.destroy)
    close_button.pack(side="right", padx=5)