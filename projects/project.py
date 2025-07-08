"""
This file is part of QuickEDL.
It provides a class to handle a QuickEDL project.
"""
import logging
from tkinter import filedialog
from pathlib import Path

class Project:
    """
    Creates and handles a QuickEDL project containing EDL file, markerlabel contents, and playlist content.
    """
    def __init__(self, update_callback=None, **kwargs):
        self.kwargs = kwargs
        
        self.project_isvalid = False
        self.update_callback = update_callback

        self.project_path = None
        self.project_name = None
        self.project_longname = None
        self.project_edl_file = None
        self.project_markerlabel_file = None
        self.project_playlist_file = None
    
    def load_project_dialog(self):
        """
        Opens a dialog to select a project folder and loads the project files.
        """
        project_path = filedialog.askdirectory(title="Select Project Folder")
        
        if project_path:
            return self.load_project_files(project_path)
        else:
            logging.error("No project folder selected")
            return False

    def load_project_files(self, project_path):
        """
        Loads the project files based on the project path.
        First tries standardized filenames, then searches for files with matching suffixes.
        """
        path = Path(project_path)
        self.project_path = path
        self.project_name = path.name

        logging.debug(f"Searching files for project: {self.project_name}")
        # Standardized filenames based on the folder name
        expected_files = {
            'edl': path / f"{self.project_name}_EDL.txt",
            'markerlabel': path / f"{self.project_name}_MARKERLABEL.txt",
            'playlist': path / f"{self.project_name}_PLAYLIST.txt"
        }

        # Check if the expected files exist
        files_found = {key: file_path for key, file_path in expected_files.items() if file_path.exists()}
        logging.debug(f"Files found by expected name: {files_found}")

        # If not all files were found, search for files with matching suffixes
        if len(files_found) < len(expected_files):
            missing_types = set(expected_files.keys()) - set(files_found.keys())
            # Search all files in the folder
            for file_path in path.iterdir():
                if file_path.is_file():
                    file_name = file_path.name.upper()
                    # Search for suffixes
                    for file_type in missing_types.copy():
                        suffix = f"_{file_type.upper()}.txt".upper()
                        if file_name.endswith(suffix):
                            files_found[file_type] = file_path
                            missing_types.remove(file_type)
                            logging.debug(f"Found file: {file_type}")
                            break
                        else :
                            logging.error(f"Missing file {file_type}")
                            break

        # Assign found files
        self.project_edl_file = files_found.get('edl')
        self.project_markerlabel_file = files_found.get('markerlabel')
        self.project_playlist_file = files_found.get('playlist')

        logging.debug(f"Final files found: {files_found}")

        # Check project validity (at least EDL file must be present)
        self.project_isvalid = self.project_edl_file is not None

        if self.project_isvalid:
            logging.info(f"Project '{self.project_name}' loaded successfully")
        else:
            logging.error(f"Project in '{project_path}' could not be loaded: EDL file missing")

        # Call update callback if provided
        if self.update_callback:
            self.update_callback()

        return self.project_isvalid

    def generate_prj_filenames(self, project_name, project_path):
        """
        Generates expected filenames based on the project name and path.
        """
        return {
            'edl': project_path / f"{project_name}_EDL.txt",
            'markerlabel': project_path / f"{project_name}_MARKERLABEL.txt",
            'playlist': project_path / f"{project_name}_PLAYLIST.txt"
        }

    def create_new_project(self, project_name, project_path, app_instance=None):
        """
        Creates a new project folder and files based on the given name and path.
        If app_instance is provided, also saves current markerlabels.
        """
        path = Path(project_path) / project_name
        path.mkdir(parents=True, exist_ok=True)

        expected_files = self.generate_prj_filenames(project_name, path)

        for file_type, file_path in expected_files.items():
            file_path.touch()
            logging.info(f"Created file: {file_path}")

        self.project_path = path
        self.project_name = project_name
        self.project_edl_file = expected_files.get('edl')
        self.project_markerlabel_file = expected_files.get('markerlabel')
        self.project_playlist_file = expected_files.get('playlist')

        self.project_isvalid = True
        logging.info(f"New project '{project_name}' created successfully at {project_path}")

        # Save current markerlabels if app_instance is provided
        if app_instance and self.project_markerlabel_file:
            try:
                # Import here to avoid circular imports
                from markerlabel import save_markerlabel
                save_markerlabel(app_instance, self.project_markerlabel_file)
                logging.info(f"Saved markerlabels to new project: {self.project_markerlabel_file}")
            except Exception as e:
                logging.error(f"Failed to save markerlabels to project: {e}")

        # Call update callback if provided
        if self.update_callback:
            self.update_callback()

        return self.project_isvalid



