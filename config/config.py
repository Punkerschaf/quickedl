import ttkbootstrap as ttk
# from pathlib import Path
import logging

from settings import get_settings_folder

class Config():
    def __init__(self, **kwargs):
        """
        Stores configuration variables of QuickEDL.
        """
        self.log_level = "INFO"
        self.settings_dir = get_settings_folder()
        self.style = ttk.Style("darkly")

        logging.info("Config initialized.")