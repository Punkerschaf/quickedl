#!/usr/bin/env python3
"""
Test script to verify that current markerlabels are saved when creating settings folder.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from settings.settings_manager import SettingsManager


def test_default_markerlabels_with_current_labels():
    """Test that current markerlabels are saved instead of hardcoded ones."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_settings_dir = Path(temp_dir) / "quickedl"
        
        # Create a mock SettingsManager that uses our temporary directory
        class TestSettingsManager(SettingsManager):
            def _get_settings_folder(self):
                return temp_settings_dir
        
        # Initialize settings manager
        settings_manager = TestSettingsManager()
        
        # Test current markerlabels (simulating user input)
        current_markerlabels = [
            "Intro Start",
            "Main Content",
            "Conclusion",
            "",  # Empty label
            "Special Moment",
            "",
            "",
            "",
            ""
        ]
        
        # Create settings folder with current markerlabels
        success = settings_manager.create_settings_folder(current_markerlabels)
        assert success, "Failed to create settings folder"
        
        # Check that the markerlabels.txt file was created
        markerlabels_file = temp_settings_dir / "markerlabels.txt"
        assert markerlabels_file.exists(), "markerlabels.txt was not created"
        
        # Read the content and verify it matches our current markerlabels
        content = markerlabels_file.read_text(encoding='utf-8')
        expected_content = "\n".join(current_markerlabels) + "\n"
        
        print("Expected content:")
        print(repr(expected_content))
        print("\nActual content:")
        print(repr(content))
        
        assert content == expected_content, f"Content mismatch!\nExpected: {repr(expected_content)}\nActual: {repr(content)}"
        
        print("✅ Test passed! Current markerlabels are correctly saved.")


def test_default_markerlabels_fallback():
    """Test that hardcoded defaults are used when no current markerlabels are provided."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_settings_dir = Path(temp_dir) / "quickedl"
        
        # Create a mock SettingsManager that uses our temporary directory
        class TestSettingsManager(SettingsManager):
            def _get_settings_folder(self):
                return temp_settings_dir
        
        # Initialize settings manager
        settings_manager = TestSettingsManager()
        
        # Create settings folder without providing current markerlabels
        success = settings_manager.create_settings_folder()
        assert success, "Failed to create settings folder"
        
        # Check that the markerlabels.txt file was created
        markerlabels_file = temp_settings_dir / "markerlabels.txt"
        assert markerlabels_file.exists(), "markerlabels.txt was not created"
        
        # Read the content and verify it matches the hardcoded defaults
        content = markerlabels_file.read_text(encoding='utf-8')
        expected_content = "\n".join([
            "Button 1 Label",
            "Button 2 Label", 
            "Button 3 Label",
            "Button 4 Label",
            "Button 5 Label",
            "Button 6 Label",
            "Button 7 Label",
            "Button 8 Label",
            "Button 9 Label",
            ""
        ])
        
        print("Expected content (fallback):")
        print(repr(expected_content))
        print("\nActual content:")
        print(repr(content))
        
        assert content == expected_content, f"Content mismatch!\nExpected: {repr(expected_content)}\nActual: {repr(content)}"
        
        print("✅ Fallback test passed! Hardcoded defaults are used when no current markerlabels provided.")


if __name__ == "__main__":
    print("Testing markerlabel saving functionality...\n")
    
    try:
        test_default_markerlabels_with_current_labels()
        print()
        test_default_markerlabels_fallback()
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
