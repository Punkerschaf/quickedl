import yaml
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa: F403
from tkinter import BooleanVar

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
    except: 
        return None
        print("Error: Could not find settings folder")

def load_yaml(app):
    """Searchs for settings.yaml in the settings folder and loads them into the app.
    Returns: Nothing. Updates variables of the app object."""
    settings_file = app.settings_folder / "settings.yaml"
    if settings_file.exists():
        with settings_file.open('r') as file:
            settings_data = yaml.safe_load(file)
            app.debug = settings_data.get('debug', app.debug)
            print("debug: ", app.debug)
            app.funny = settings_data.get('funny', app.funny)
            print("funny: ", app.funny)
            app.default_dir = settings_data.get('default_dir', app.default_dir)
            print("default_dir: ", app.default_dir)
    else:
        print("Error: Could not find settings file")
        return

#######################
### Settings WINDOW ###
#######################

def show_settings_window(app):
    """Shows the settings window of the app object."""
    settings_window = ttk.Toplevel(app.root)
    settings_window.title("QuickEDL: Settings")
    settings_window.geometry("400x250")

    def update_folder_indicator(app, folder_indicator):
        if app.settings_folder.exists():
            folder_indicator.config(text="found", bootstyle="success")
        else:
            return

# settings folder
    settings_folder_frame = ttk.LabelFrame(settings_window, text=" settings folder")
    settings_folder_frame.pack(padx= 10, pady=5, fill='x',)
    folder_label = ttk.Label(settings_folder_frame, textvariable=app.settings_folder_str, justify=LEFT)
    folder_label.pack(padx=5)
    folder_indicator = ttk.Label(settings_folder_frame, text="not found", bootstyle="warning")
    folder_indicator.pack()
    update_folder_indicator(app, folder_indicator)


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
    close_button = ttk.Button(confirmation_frame, text="Close")
    close_button.pack(side=RIGHT, padx=5)
    close_button.bind("<Button-1>", lambda: settings_window.destroy())