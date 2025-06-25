import logging

from pathlib import Path

class Project:
    """
    Creates and handles a QuickEDL project containing EDL file, entry contents, and playlist content.
    """
    def __init__(self, default_path, **kwargs):
        self.kwargs = kwargs.get
        
        self.project_isvalid = False

        self.project_path = None
        self.project_name = None
        self.project_longname = None
        self.project_edl_file = None
        self.project_texts_file = None
        self.project_playlist_file = None
    
    def load_project_files(self, project_path):
            """
            Loads the project files based on the project path.
            First tries standardized filenames, then searches for files with matching suffixes.
            """
            path = Path(project_path)
            self.project_path = path
            self.project_name = path.name
            
            # Standardized filenames based on the folder name
            expected_files = {
                'edl': path / f"{self.project_name}_EDL.txt",
                'texts': path / f"{self.project_name}_TEXTS.txt",
                'playlist': path / f"{self.project_name}_PLAYLIST.txt"
            }
            
            # Check if the expected files exist
            files_found = {key: file_path for key, file_path in expected_files.items() if file_path.exists()}
            
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
                                break
            
            # Assign found files
            self.project_edl_file = files_found.get('edl')
            self.project_texts_file = files_found.get('texts')
            self.project_playlist_file = files_found.get('playlist')
            
            # Check project validity (at least EDL file must be present)
            self.project_isvalid = self.project_edl_file is not None
            
            if self.project_isvalid:
                logging.info(f"Project '{self.project_name}' loaded successfully")
            else:
                logging.error(f"Project in '{project_path}' could not be loaded: EDL file missing")
                
            return self.project_isvalid