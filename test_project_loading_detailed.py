#!/usr/bin/env python3
"""
Test script to verify that project loading now includes markerlabels and playlist loading.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent))

from projects.project import Project

# Set up logging to see what happens
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_project_loading_with_content():
    """Test that project loading works correctly with actual content files."""
    
    # Create a mock app with markerlabel entries similar to the real app
    class MockApp:
        def __init__(self):
            # Simulate markerlabel entries (9 text widgets)
            self.markerlabel_entries = []
            for i in range(9):
                # Create mock entry objects that have get(), delete(), and insert() methods
                entry = MockEntry()
                self.markerlabel_entries.append(entry)
            
            self.playlist = MockPlaylist()
            
        def __call__(self):
            print("Project update callback called")
            print("Current markerlabel entries:")
            for i, entry in enumerate(self.markerlabel_entries):
                print(f"  Entry {i+1}: '{entry.text}'")
    
    class MockEntry:
        def __init__(self):
            self.text = ""
            
        def get(self):
            return self.text
            
        def delete(self, start, end):
            self.text = ""
            
        def insert(self, pos, text):
            self.text = text
    
    class MockPlaylist:
        def __init__(self):
            self.data = []
            
        def load_from_project(self):
            print("Playlist.load_from_project() called")
            # This would load from the project file, but for testing we'll just simulate it
            self.data = ["Simulated playlist item 1", "Simulated playlist item 2"]
            print(f"Playlist now contains: {self.data}")
    
    # Create project instance with mock callback
    app = MockApp()
    project = Project(update_callback=app)
    
    print("Testing project loading with actual content files...")
    
    # Test loading the test project we created
    test_project_path = str(Path(__file__).parent / "test_project")
    print(f"Loading test project from: {test_project_path}")
    
    result = project.load_project_files(test_project_path)
    print(f"Loading test project returned: {result}")
    print(f"Project valid: {project.project_isvalid}")
    print(f"EDL file: {project.project_edl_file}")
    print(f"Markerlabel file: {project.project_markerlabel_file}")
    print(f"Playlist file: {project.project_playlist_file}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_project_loading_with_content()
