import os
import logging

def debug(debug, msg):
    if debug:
        print(msg)

def open_directory(path):
    """Opens a path in a explorer/finder window.
    Args:
        path: path to open
    """
    if os.name == 'nt':
        os.startfile(path)
    elif os.name == 'posix':
        os.system(f'open "{path}"')
    else:
        logging.error("Unsupported OS")