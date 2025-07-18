#!/usr/bin/env python3
"""
Test script for Recent Projects functionality
"""

import sys
import tempfile
from pathlib import Path

# Add the current directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from settings.recent import RecentProjectsManager


def test_recent_projects():
    """Test the recent projects functionality."""
    print("Testing Recent Projects Manager...")
    
    # Create temporary settings folder
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_settings = Path(temp_dir) / "settings"
        temp_settings.mkdir()
        
        # Create mock settings manager
        class MockSettingsManager:
            def __init__(self, settings_folder):
                self.settings_folder = settings_folder
            
            def get_settings_folder_path(self):
                return self.settings_folder
        
        mock_settings = MockSettingsManager(temp_settings)
        
        # Test RecentProjectsManager
        manager = RecentProjectsManager(mock_settings, max_recent=3)
        
        # Test 1: Check if available
        print(f"Recent projects available: {manager.is_available()}")
        assert manager.is_available(), "Recent projects should be available"
        
        # Test 2: Load empty list
        projects = manager.load_recent_projects()
        print(f"Initial projects: {projects}")
        assert projects == [], "Initial list should be empty"
        
        # Test 3: Add projects
        manager.add_project("Test Project 1", "/path/to/project1")
        manager.add_project("Test Project 2", "/path/to/project2")
        manager.add_project("Test Project 3", "/path/to/project3")
        
        projects = manager.load_recent_projects()
        print(f"After adding 3 projects: {projects}")
        assert len(projects) == 3, "Should have 3 projects"
        assert projects[0]['name'] == "Test Project 3", "Most recent should be first"
        
        # Test 4: Add more than max_recent
        manager.add_project("Test Project 4", "/path/to/project4")
        
        projects = manager.load_recent_projects()
        print(f"After adding 4th project: {projects}")
        assert len(projects) == 3, "Should still have only 3 projects"
        assert projects[0]['name'] == "Test Project 4", "Newest should be first"
        assert "Test Project 1" not in [p['name'] for p in projects], "Oldest should be removed"
        
        # Test 5: Re-add existing project (should move to top)
        manager.add_project("Test Project 2", "/path/to/project2")
        
        projects = manager.load_recent_projects()
        print(f"After re-adding project 2: {projects}")
        assert projects[0]['name'] == "Test Project 2", "Re-added project should be first"
        assert len(projects) == 3, "Should still have only 3 projects"
        
        # Test 6: Remove project
        manager.remove_project("/path/to/project2")
        
        projects = manager.load_recent_projects()
        print(f"After removing project 2: {projects}")
        assert len(projects) == 2, "Should have 2 projects after removal"
        assert "Test Project 2" not in [p['name'] for p in projects], "Removed project should not be in list"
        
        # Test 7: Update max_recent
        manager.update_max_recent(1)
        
        projects = manager.load_recent_projects()
        print(f"After setting max_recent to 1: {projects}")
        assert len(projects) == 1, "Should have only 1 project after reducing max"
        
        print("✅ All tests passed!")


if __name__ == "__main__":
    test_recent_projects()
