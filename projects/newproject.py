"""
This file is part of QuickEDL.
"""
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from tkinter import filedialog
from pathlib import Path
import logging

def show_new_project_window(root, project):
    """
    Opens a window to create a new project.
    Takes ttk-root and project
    """
    def create_project():
        project_name = name_entry.get().strip()
        project_path_str = location_entry.get().strip()

        if not project_name or not project_path_str:
            logging.error("Project name or location is missing.")
            return

        try:
            # Convert to Path object for platform-independent handling
            project_path = Path(project_path_str)
            
            # Validate that the path exists and is a directory
            if not project_path.exists():
                logging.error(f"Selected path does not exist: {project_path}")
                Messagebox.show_error("Error", f"The selected path does not exist:\n{project_path}")
                return
            
            if not project_path.is_dir():
                logging.error(f"Selected path is not a directory: {project_path}")
                Messagebox.show_error("Error", f"The selected path is not a directory:\n{project_path}")
                return
            
            # Check if project folder would already exist
            new_project_path = project_path / project_name
            if new_project_path.exists():
                logging.warning(f"Project folder already exists: {new_project_path}")
                result = Messagebox.show_question(
                    "Project Exists", 
                    f"A folder named '{project_name}' already exists in the selected location.\nDo you want to continue anyway?"
                )
                if result != "Yes":
                    return
            
            # Pass the string representation to maintain compatibility with existing code
            project.create_new_project(project_name, str(project_path))
            logging.info(f"Project '{project_name}' created at '{project_path}'.")
            new_project_window.destroy()
        except Exception as e:
            logging.error(f"Failed to create project: {e}")
            Messagebox.show_error("Error", f"Failed to create project:\n{str(e)}")

    def select_location():
        folder = filedialog.askdirectory(title="Select Project Location")
        if folder:
            # Convert to Path object for platform-independent handling
            folder_path = Path(folder)
            location_entry.delete(0, 'end')
            # Use the resolved absolute path for consistency
            location_entry.insert(0, str(folder_path.resolve()))
            validate_inputs()

    def validate_inputs(*args):
        """
        Validates the inputs and enables/disables the Create button.
        """
        project_name = name_entry.get().strip()
        project_path_str = location_entry.get().strip()

        # Basic validation: both fields must be filled
        if not project_name or not project_path_str:
            create_button.config(state="disabled")
            return

        # Validate project name (no invalid characters for file/folder names)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in project_name for char in invalid_chars):
            create_button.config(state="disabled")
            return

        # Validate path exists if it's not empty
        try:
            project_path = Path(project_path_str)
            if project_path_str and not project_path.exists():
                create_button.config(state="disabled")
                return
        except (OSError, ValueError):
            # Invalid path format
            create_button.config(state="disabled")
            return

        # All validations passed
        create_button.config(state="normal")

    new_project_window = ttk.Toplevel(root)
    new_project_window.title("Create New Project")

    ttk.Label(new_project_window, text="Project Name:", bootstyle="primary").grid(row=0, column=0, padx=10, pady=10)
    name_entry = ttk.Entry(new_project_window, width=30, bootstyle="info")
    name_entry.grid(row=0, column=1, padx=10, pady=10)
    name_entry.bind("<KeyRelease>", validate_inputs)

    ttk.Label(new_project_window, text="Project Location:", bootstyle="primary").grid(row=1, column=0, padx=10, pady=10)
    location_entry = ttk.Entry(new_project_window, width=30, bootstyle="info")
    location_entry.grid(row=1, column=1, padx=10, pady=10)
    location_entry.bind("<KeyRelease>", validate_inputs)

    ttk.Button(new_project_window, text="Browse", command=select_location, bootstyle="secondary").grid(row=1, column=2, padx=10, pady=10)
    create_button = ttk.Button(new_project_window, text="Create", command=create_project, bootstyle="success", state="disabled")
    create_button.grid(row=2, column=0, columnspan=3, pady=20)

    new_project_window.transient(root)
    new_project_window.grab_set()
    new_project_window.mainloop()

