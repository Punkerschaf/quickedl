#!/usr/bin/env python3
"""
Test script to verify the "Save markerlabels to defaults" functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from settings.settings_manager import SettingsManager


def test_save_markerlabels_to_defaults_method():
    """Test that the save_current_markerlabels_to_default method works correctly."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_settings_dir = Path(temp_dir) / "quickedl"
        
        # Create a mock SettingsManager that uses our temporary directory
        class TestSettingsManager(SettingsManager):
            def _get_settings_folder(self):
                return temp_settings_dir
        
        # Initialize settings manager
        settings_manager = TestSettingsManager()
        
        # Test markerlabels from GUI
        test_markerlabels = [
            "Custom Label 1",
            "Custom Label 2",
            "Test Label",
            "",  # Empty label
            "Important Moment",
            "",
            "",
            "Final Label",
            ""
        ]
        
        # Test the save method
        success = settings_manager.save_current_markerlabels_to_default(test_markerlabels)
        assert success, "Failed to save markerlabels to default"
        
        # Check that the markerlabels.txt file was created
        markerlabels_file = temp_settings_dir / "markerlabels.txt"
        assert markerlabels_file.exists(), "markerlabels.txt was not created"
        
        # Read the content and verify it matches our test markerlabels
        content = markerlabels_file.read_text(encoding='utf-8')
        expected_content = "\n".join(test_markerlabels) + "\n"
        
        print("Test markerlabels:")
        for i, label in enumerate(test_markerlabels, 1):
            print(f"  {i}: '{label}'")
        
        print("\nExpected content:")
        print(repr(expected_content))
        print("\nActual content:")
        print(repr(content))
        
        assert content == expected_content, f"Content mismatch!\nExpected: {repr(expected_content)}\nActual: {repr(content)}"
        
        print("✅ Test passed! save_current_markerlabels_to_default works correctly.")


def test_settings_folder_creation_with_markerlabels():
    """Test that when creating settings folder, current markerlabels are used."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_settings_dir = Path(temp_dir) / "quickedl"
        
        # Create a mock SettingsManager that uses our temporary directory
        class TestSettingsManager(SettingsManager):
            def _get_settings_folder(self):
                return temp_settings_dir
        
        # Initialize settings manager
        settings_manager = TestSettingsManager()
        
        # Test markerlabels that would come from GUI during first setup
        startup_markerlabels = [
            "",  # Empty at startup
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
        ]
        
        # Create settings folder with startup markerlabels (all empty)
        success = settings_manager.create_settings_folder(startup_markerlabels)
        assert success, "Failed to create settings folder"
        
        # Check that the markerlabels.txt file was created
        markerlabels_file = temp_settings_dir / "markerlabels.txt"
        assert markerlabels_file.exists(), "markerlabels.txt was not created"
        
        # Read the content and verify it matches our startup markerlabels (empty)
        content = markerlabels_file.read_text(encoding='utf-8')
        expected_content = "\n".join(startup_markerlabels) + "\n"
        
        print("Startup markerlabels (empty):")
        print(repr(expected_content))
        print("\nActual content:")
        print(repr(content))
        
        assert content == expected_content, f"Content mismatch!\nExpected: {repr(expected_content)}\nActual: {repr(content)}"
        
        print("✅ Test passed! Settings folder creation uses current markerlabels correctly.")


if __name__ == "__main__":
    print("Testing markerlabel saving functionality...\n")
    
    try:
        test_save_markerlabels_to_defaults_method()
        print()
        test_settings_folder_creation_with_markerlabels()
        print("\n🎉 All tests passed! The implementation works correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
