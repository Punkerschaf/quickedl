"""
This file is part of QuickEDL.
It handles functions to save and load the markerlabels in the project.
"""

import logging
from pathlib import Path
from tkinter import END


def save_markerlabel(self, save_path):
    """
    Saves the markerlabels to a file.
    Takes path-object.
    """
    if save_path:
        save_path = Path(save_path)
        save_path.write_text("\n".join(entry.get() for entry in self.markerlabel_entries) + "\n")
        logging.info("Saved markerlabels to project.")
    else:
        logging.error("No path to save markerlabels.")

def load_markerlabel(self, load_path, startup_toast=None):
    """
    Loads the markerlabels from a file.
    Takes path-object.
    """
    if load_path:
        load_path = Path(load_path)
        lines = load_path.read_text().splitlines()
        for i, line in enumerate(lines[:9]):
            self.markerlabel_entries[i].delete(0, END)
            self.markerlabel_entries[i].insert(0, line.strip())
        logging.debug("Loaded markerlabels from project.")
        if startup_toast:
            startup_toast.addline("Markerlabels loaded.")
    else:
        logging.error("No path to load markerlabels.")