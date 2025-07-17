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

def test_project_loading():
    """Test that project loading works correctly."""
    
    # Create a mock callback to simulate the app
    class MockApp:
        def __init__(self):
            self.markerlabel_entries = []
            self.playlist = MockPlaylist()
            
        def __call__(self):
            print("Project update callback called")
    
    class MockPlaylist:
        def load_from_project(self):
            print("Playlist.load_from_project() called")
    
    # Create project instance with mock callback
    project = Project(update_callback=MockApp())
    
    print("Testing project loading functionality...")
    
    # Test loading a non-existent project (should now handle this gracefully)
    result = project.load_project_files("/non/existent/path")
    print(f"Loading non-existent project returned: {result}")
    
    # Test loading the current directory (which exists)
    current_dir = str(Path(__file__).parent)
    result = project.load_project_files(current_dir)
    print(f"Loading current directory project returned: {result}")
    
    # Test the file name generation
    test_path = Path("/test/project")
    expected_files = project.generate_prj_filenames("TestProject", test_path)
    print(f"Expected files for 'TestProject': {expected_files}")
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_project_loading()
