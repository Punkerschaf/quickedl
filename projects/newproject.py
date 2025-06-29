"""
This file is part of QuickEDL.
"""
import ttkbootstrap as ttk

from tkinter import filedialog, StringVar
from pathlib import Path
import logging
import sys

def show_new_project_window(root, project):
    """
    Opens a window to create a new project.
    Takes ttk-root and project
    """
    def create_project():
        project_name = name_entry.get()
        project_path = location_entry.get()

        if not project_name or not project_path:
            logging.error("Project name or location is missing.")
            return

        try:
            project.create_new_project(project_name, project_path)
            logging.info(f"Project '{project_name}' created at '{project_path}'.")
            new_project_window.destroy()
        except Exception as e:
            logging.error(f"Failed to create project: {e}")

    def select_location():
        folder = filedialog.askdirectory(title="Select Project Location")
        if folder:
            location_entry.delete(0, 'end')
            location_entry.insert(0, folder)

    new_project_window = ttk.Toplevel(root)
    new_project_window.title("Create New Project")

    ttk.Label(new_project_window, text="Project Name:", bootstyle="primary").grid(row=0, column=0, padx=10, pady=10)
    name_entry = ttk.Entry(new_project_window, width=30, bootstyle="info")
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(new_project_window, text="Project Location:", bootstyle="primary").grid(row=1, column=0, padx=10, pady=10)
    location_entry = ttk.Entry(new_project_window, width=30, bootstyle="info")
    location_entry.grid(row=1, column=1, padx=10, pady=10)

    ttk.Button(new_project_window, text="Browse", command=select_location, bootstyle="secondary").grid(row=1, column=2, padx=10, pady=10)
    ttk.Button(new_project_window, text="Create", command=create_project, bootstyle="success").grid(row=2, column=0, columnspan=3, pady=20)

    new_project_window.transient(root)
    new_project_window.grab_set()
    new_project_window.mainloop()

