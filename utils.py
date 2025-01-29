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
        directory = Path(path)
        if not directory.exists():
            logging.error(f"Directory does not exist: {directory}")
            return
        if not directory.is_dir():
            logging.error(f"Path is not a directory: {directory}")
            return
        if os.name == 'nt':
            subprocess.run(['explorer', str(directory)])
        elif os.name == 'posix':
            subprocess.run(['open', str(directory)])
        else:
            logging.error("Unsupported OS")
    except Exception as e:
        logging.error(f"An error occurred while opening the directory: {e}", exc_info=True)