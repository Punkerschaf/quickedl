import os
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from tkinter import filedialog, StringVar

#######################
### SETTINGS FOLDER ###
#######################

def get_settings_folder():
    try:
        home_dir = Path.home()
        settings_folder = home_dir  / "quickedl"
        return settings_folder
    except: 
        return None
        print("Error: Could not find settings folder")

def folder_indicator_style(app):
    if app.settings_folder.exists():
        return "success"
    else:
        return "warning-outline"

#######################
### Settings WINDOW ###
#######################
def show_settings_window(app):
    settings_window = ttk.Toplevel(app.root)
    settings_window.title("QuickEDL: Settings")
    settings_window.geometry("400x500")

# settings folder
    settings_folder_frame = ttk.LabelFrame(settings_window, text=" settings folder")
    settings_folder_frame.pack(padx= 10, pady=5, fill='x',)
    folder_label = ttk.Label(settings_folder_frame, textvariable=app.settings_folder_str, justify=LEFT)
    folder_label.pack(padx=5, pady=5)
    indicator_frame = ttk.Frame(settings_folder_frame)
    indicator_frame.pack(anchor=W, pady=5)
    folder_indicator = ttk.Button(indicator_frame, text="settings folder", state="active",
                                  bootstyle=folder_indicator_style(app))
    folder_indicator.pack(padx=5)

# default edl path
    default_edl_frame = ttk.LabelFrame(settings_window, text=" default EDL path ")
    default_edl_frame.pack(padx=10, pady=5, fill='x')
    default_path_label = ttk.Label(default_edl_frame, text="not implemented yet", bootstyle="warning")
    default_path_label.pack(pady=5)

# misc settings
    misc_frame = ttk.LabelFrame(settings_window, text=" misc ")
    misc_frame.pack(padx=10, pady=5, fill='x')
    funny_toggle = ttk.Checkbutton(misc_frame, text="funny mode", bootstyle="success-square-toggle")
    funny_toggle.pack(pady=5)

# close Button
    confirmation_frame = ttk.Frame(settings_window)
    confirmation_frame.pack(pady=5)
    close_button = ttk.Button(confirmation_frame, text="Close")
    close_button.pack(side=RIGHT, padx=5)
    close_button.bind("<Button-1>", lambda event: settings_window.destroy())