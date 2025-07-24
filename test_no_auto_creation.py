#!/usr/bin/env python3
"""
Test script to verify that settings folder is NOT automatically created.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from settings.settings_manager import SettingsManager


def test_no_automatic_folder_creation():
    """Test that settings operations do not automatically create the folder."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_settings_dir = Path(temp_dir) / "quickedl"
        
        # Create a mock SettingsManager that uses our temporary directory
        class TestSettingsManager(SettingsManager):
            def _get_settings_folder(self):
                return temp_settings_dir
        
        # Initialize settings manager
        settings_manager = TestSettingsManager()
        
        # Verify folder doesn't exist initially
        assert not temp_settings_dir.exists(), "Settings folder should not exist initially"
        
        # Test 1: load_settings should not create folder
        settings = settings_manager.load_settings()
        assert not temp_settings_dir.exists(), "load_settings should not create settings folder"
        print("✅ load_settings does not create folder")
        
        # Test 2: save_settings should not create folder
        success = settings_manager.save_settings(settings)
        assert not success, "save_settings should fail when folder doesn't exist"
        assert not temp_settings_dir.exists(), "save_settings should not create settings folder"
        print("✅ save_settings does not create folder and returns False")
        
        # Test 3: save_current_markerlabels_to_default should not create folder
        test_labels = ["Label 1", "", "Label 3", "", "", "", "", "", ""]
        success = settings_manager.save_current_markerlabels_to_default(test_labels)
        assert not success, "save_current_markerlabels_to_default should fail when folder doesn't exist"
        assert not temp_settings_dir.exists(), "save_current_markerlabels_to_default should not create settings folder"
        print("✅ save_current_markerlabels_to_default does not create folder and returns False")
        
        # Test 4: Only create_settings_folder should create the folder
        success = settings_manager.create_settings_folder(test_labels)
        assert success, "create_settings_folder should succeed"
        assert temp_settings_dir.exists(), "create_settings_folder should create the folder"
        print("✅ create_settings_folder creates folder successfully")
        
        # Test 5: After manual creation, other operations should work
        success = settings_manager.save_current_markerlabels_to_default(test_labels)
        assert success, "save_current_markerlabels_to_default should work after folder creation"
        
        markerlabels_file = temp_settings_dir / "markerlabels.txt"
        assert markerlabels_file.exists(), "markerlabels.txt should be created"
        print("✅ Operations work correctly after manual folder creation")
        
        print("\n🎉 All tests passed! Settings folder is only created manually.")


if __name__ == "__main__":
    print("Testing that settings folder is NOT automatically created...\n")
    
    try:
        test_no_automatic_folder_creation()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
