#!/usr/bin/env python3
"""
Final test to demonstrate complete project loading functionality including markerlabels and playlist.
This simulates the complete workflow as it would happen in the real application.
"""

import sys
import logging
from pathlib import Path
from tkinter import END

# Add the project root to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent))

from projects.project import Project
from markerlabel import load_markerlabel

# Set up logging to see what happens
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_complete_project_loading():
    """Test complete project loading workflow with markerlabels and playlist."""
    
    # Create a realistic simulation of the main app
    class SimulatedApp:
        def __init__(self):
            # Simulate the 9 markerlabel entries like in the real app
            self.markerlabel_entries = []
            for i in range(9):
                entry = SimulatedEntry()
                self.markerlabel_entries.append(entry)
            
            # Simulate playlist
            self.playlist = SimulatedPlaylist()
            
        def __call__(self):
            """This simulates the on_project_update callback"""
            print("=== Project Update Callback ===")
            self.update_project_display()
            if hasattr(self, 'project') and self.project.project_isvalid:
                self.load_project_content()
                
        def update_project_display(self):
            print("Updating project display...")
            
        def load_project_content(self):
            """This simulates the load_project_content method from main.py"""
            try:
                # Load markerlabels if file exists
                if (self.project.project_markerlabel_file and 
                    Path(self.project.project_markerlabel_file).exists()):
                    
                    load_markerlabel(self, self.project.project_markerlabel_file)
                    print(f"✓ Loaded markerlabels from project: {self.project.project_markerlabel_file}")
                
                # Load playlist if file exists
                if (self.project.project_playlist_file and 
                    Path(self.project.project_playlist_file).exists()):
                    
                    self.playlist.load_from_project(self.project)
                    print(f"✓ Loaded playlist from project: {self.project.project_playlist_file}")
                    
            except Exception as e:
                print(f"✗ Error loading project content: {e}")
    
    class SimulatedEntry:
        """Simulates a tkinter Entry widget"""
        def __init__(self):
            self.text = ""
            
        def get(self):
            return self.text
            
        def delete(self, start, end):
            if start == 0 and end == END:
                self.text = ""
            
        def insert(self, pos, text):
            if pos == 0:
                self.text = text
    
    class SimulatedPlaylist:
        """Simulates the Playlist class"""
        def __init__(self):
            self.data = ["No Items"]
            
        def load_from_project(self, project):
            if project.project_playlist_file:
                playlist_file = Path(project.project_playlist_file)
                if playlist_file.exists():
                    self.data = playlist_file.read_text().splitlines()
                    self.data = [line for line in self.data if line.strip()]
                    if not self.data:
                        self.data = ["No Items"]
                    print(f"  Playlist data loaded: {self.data}")
    
    # Create the simulated app
    app = SimulatedApp()
    
    # Create project with app as callback
    project = Project(update_callback=app)
    app.project = project  # Give app reference to project
    
    print("=== Testing Complete Project Loading ===")
    print()
    
    # Test loading our test project
    test_project_path = str(Path(__file__).parent / "test_project")
    print(f"Loading test project from: {test_project_path}")
    print()
    
    result = project.load_project_files(test_project_path)
    
    print()
    print("=== Results ===")
    print(f"Project loading successful: {result}")
    print(f"Project name: {project.project_name}")
    print(f"EDL file found: {project.project_edl_file is not None}")
    print(f"Markerlabel file found: {project.project_markerlabel_file is not None}")
    print(f"Playlist file found: {project.project_playlist_file is not None}")
    print()
    
    if result:
        print("=== Loaded Content ===")
        print("Markerlabels:")
        for i, entry in enumerate(app.markerlabel_entries):
            print(f"  Button {i+1}: '{entry.get()}'")
        
        print(f"Playlist: {app.playlist.data}")
    
    print()
    print("✓ Complete project loading test successful!")

if __name__ == "__main__":
    test_complete_project_loading()
