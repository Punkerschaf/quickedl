#!/usr/bin/env python3
"""
Test script to verify that playlist GUI updates work correctly after loading from project.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent))

from projects.project import Project
from playlist import Playlist

# Set up logging to see what happens
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_playlist_gui_update():
    """Test that playlist GUI updates correctly after loading from project."""
    
    # Create test project and files
    test_project_path = Path(__file__).parent / "test_playlist_project"
    test_project_path.mkdir(exist_ok=True)
    
    # Create project files
    (test_project_path / "test_playlist_project_EDL.txt").write_text("19:45:12 - Test marker\n")
    (test_project_path / "test_playlist_project_PLAYLIST.txt").write_text("Test Song 1\nTest Song 2\nTest Song 3\n")
    
    print("=== Testing Playlist GUI Updates ===")
    
    # Create project
    project = Project()
    result = project.load_project_files(str(test_project_path))
    print(f"Project loaded: {result}")
    print(f"Playlist file: {project.project_playlist_file}")
    
    # Create playlist with mock StringVar for testing
    class MockStringVar:
        def __init__(self, value=""):
            self.value = value
            
        def set(self, value):
            self.value = value
            print(f"  GUI Updated - playhead_text set to: '{value}'")
            
        def get(self):
            return self.value
    
    class MockIntVar:
        def __init__(self, value=0):
            self.value = value
            self._callbacks = []
            
        def set(self, value):
            old_value = self.value
            self.value = value
            if old_value != value:
                print(f"  GUI Updated - playhead set to: {value}")
                # Trigger callbacks
                for callback in self._callbacks:
                    callback()
                    
        def get(self):
            return self.value
            
        def trace_add(self, mode, callback):
            self._callbacks.append(callback)
    
    # Create playlist instance
    playlist = Playlist(project=project)
    
    # Replace the StringVar and IntVar with mock versions for testing
    playlist.playhead_text = MockStringVar("Initial Value")
    playlist.playhead = MockIntVar(0)
    playlist.playhead.trace_add("write", playlist.on_playhead_update)
    
    print(f"\nBefore loading - playhead_text: '{playlist.playhead_text.get()}'")
    print(f"Before loading - data: {playlist.data}")
    
    # Load from project
    print("\n--- Loading playlist from project ---")
    playlist.load_from_project()
    
    print(f"\nAfter loading - playhead_text: '{playlist.playhead_text.get()}'")
    print(f"After loading - data: {playlist.data}")
    print(f"After loading - playhead position: {playlist.playhead.get()}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_project_path)
    
    print("\n✓ Playlist GUI update test completed!")

if __name__ == "__main__":
    test_playlist_gui_update()
