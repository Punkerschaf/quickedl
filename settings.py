import os
from pathlib import Path

def get_settings_folder():
    try:
        home_dir = Path.home()
        settings_folder = home_dir  / "quickedl"
        return settings_folder
    except: 
        return None
        print("Error: Could not find settings folder")

def create_settings_folder():
    settings_folder = get_settings_folder()
    if not settings_folder.exists():
        settings_folder.mkdir(parents=True)
    return settings_folder