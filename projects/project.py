import logging

from pathlib import Path

class Project:
    """
    creates and handles a QuickEDL-project containing EDL-file, entry-contents and playlist content.
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
            Lädt die Projektdateien basierend auf dem Projektpfad.
            Versucht zuerst standardisierte Dateinamen, dann sucht nach Dateien mit passenden Suffixen.
            """
            path = Path(project_path)
            self.project_path = path
            self.project_name = path.name
            
            # Standardisierte Dateinamen basierend auf dem Ordnernamen
            expected_files = {
                'edl': path / f"{self.project_name}_EDL.txt",
                'texts': path / f"{self.project_name}_TEXTS.txt",
                'playlist': path / f"{self.project_name}_PLAYLIST.txt"
            }
            
            # Prüfen, ob die erwarteten Dateien existieren
            files_found = {key: file_path for key, file_path in expected_files.items() if file_path.exists()}
            
            # Falls nicht alle Dateien gefunden wurden, suche nach Dateien mit passenden Suffixen
            if len(files_found) < len(expected_files):
                missing_types = set(expected_files.keys()) - set(files_found.keys())
                
                # Alle Dateien im Ordner durchsuchen
                for file_path in path.iterdir():
                    if file_path.is_file():
                        file_name = file_path.name.upper()
                        
                        # Nach Suffixen suchen
                        for file_type in missing_types.copy():
                            suffix = f"_{file_type.upper()}.txt".upper()
                            if file_name.endswith(suffix):
                                files_found[file_type] = file_path
                                missing_types.remove(file_type)
                                break
            
            # Gefundene Dateien zuweisen
            self.project_edl_file = files_found.get('edl')
            self.project_texts_file = files_found.get('texts')
            self.project_playlist_file = files_found.get('playlist')
            
            # Projektgültigkeit prüfen (mindestens EDL-Datei muss vorhanden sein)
            self.project_isvalid = self.project_edl_file is not None
            
            if self.project_isvalid:
                logging.info(f"Projekt '{self.project_name}' erfolgreich geladen")
            else:
                logging.error(f"Projekt in '{project_path}' konnte nicht geladen werden: EDL-Datei fehlt")
                
            return self.project_isvalid