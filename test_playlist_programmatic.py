#!/usr/bin/env python3
"""
Test script to programmatically test playlist loading and GUI updates.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from projects.project import Project

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_playlist_loading():
    """Test playlist loading programmatically."""
    
    class MockApp:
        def __init__(self):
            # Simulate markerlabel entries
            self.markerlabel_entries = []
            for i in range(9):
                entry = MockEntry()
                self.markerlabel_entries.append(entry)
            
            # Important: Initialize playlist AFTER project
            self.project = None
            self.playlist = None
            
        def on_project_update(self):
            print("=== Project Update Callback ===")
            self.update_project_display()
            if self.project.project_isvalid:
                self.load_project_content()
                
        def update_project_display(self):
            print(f"Project display updated: {self.project.project_name}")
            
        def load_project_content(self):
            try:
                # Load markerlabels if file exists
                if (self.project.project_markerlabel_file and 
                    Path(self.project.project_markerlabel_file).exists()):
                    
                    from markerlabel import load_markerlabel
                    load_markerlabel(self, self.project.project_markerlabel_file)
                    print(f"✓ Loaded markerlabels from: {self.project.project_markerlabel_file}")
                
                # Load playlist if file exists
                if (self.project.project_playlist_file and 
                    Path(self.project.project_playlist_file).exists()):
                    
                    print(f"Before playlist load - data: {self.playlist.data}")
                    print(f"Before playlist load - playhead_text: '{self.playlist.playhead_text.get()}'")
                    
                    self.playlist.load_from_project()
                    
                    print(f"After playlist load - data: {self.playlist.data}")
                    print(f"After playlist load - playhead_text: '{self.playlist.playhead_text.get()}'")
                    print(f"✓ Loaded playlist from: {self.project.project_playlist_file}")
                    
            except Exception as e:
                print(f"✗ Error loading project content: {e}")
    
    class MockEntry:
        def __init__(self):
            self.text = ""
            
        def get(self):
            return self.text
            
        def delete(self, start, end):
            self.text = ""
            
        def insert(self, pos, text):
            self.text = text
    
    # Create mock app
    app = MockApp()
    
    # Create project
    project = Project(update_callback=app.on_project_update)
    app.project = project
    
    # Create playlist with proper StringVar mock
    from playlist import Playlist
    
    # We need to mock the StringVar and IntVar properly
    class MockStringVar:
        def __init__(self, value=""):
            self.value = value
            
        def set(self, value):
            old_value = self.value
            self.value = value
            if old_value != value:
                print(f"  → GUI Updated: playhead_text = '{value}'")
            
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
                print(f"  → GUI Updated: playhead = {value}")
                # Trigger all callbacks
                for callback in self._callbacks:
                    try:
                        callback()
                    except Exception as e:
                        print(f"    Callback error: {e}")
            
        def get(self):
            return self.value
            
        def trace_add(self, mode, callback):
            self._callbacks.append(callback)
    
    # Create playlist with mocked variables
    print("Creating playlist...")
    playlist = Playlist(project=project)
    
    # Replace StringVar and IntVar with our mocks
    playlist.playhead_text = MockStringVar("Initial Value")
    old_playhead = playlist.playhead
    playlist.playhead = MockIntVar(0)
    
    # Re-register the callbacks
    playlist.playhead.trace_add("write", playlist.on_playhead_update)
    playlist.playhead.trace_add("write", playlist.update_decinc_able)
    
    app.playlist = playlist
    
    print("\n=== Testing Project Loading ===")
    test_project_path = str(Path(__file__).parent / "test_playlist_gui_project")
    
    # Load the project (this should trigger the GUI updates)
    result = project.load_project_files(test_project_path)
    
    print(f"\nProject loading result: {result}")
    
    # Clean up
    import shutil
    try:
        shutil.rmtree(Path(__file__).parent / "test_playlist_gui_project")
        print("\nCleaned up test files")
    except:
        pass
    
    print("\n✓ Test completed!")

if __name__ == "__main__":
    test_playlist_loading()
