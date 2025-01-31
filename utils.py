import subprocess
from pathlib import Path
import os
import logging

def debug(debug, msg):
    if debug:
        print(msg)

def open_directory(path):
    """
    Opens a path in a explorer/finder window.
    Args:
        path: path to open
    """
    try:
        path = Path(path)
        if not path.exists():
            logging.error(f"PAth does not exist: {path}")
            return
        if path.is_dir():
            directory = path
        else:
            directory = path.parent
        
        if os.name == 'nt': # Windows
            if path.is_dir():
                subprocess.run(['explorer', str(directory)])
            else:
                subprocess.run(['explorer', '/select,', str(path)])

        elif os.name == 'posix': # Unix
            if path.is_dir():
                subprocess.run(['open', str(directory)])
            else:
                subprocess.run(['open', '-R', str(path)])
        else:
            logging.error("Unsupported OS")
    except Exception as e:
        logging.error(f"An error occurred while opening the directory: {e}", exc_info=True)