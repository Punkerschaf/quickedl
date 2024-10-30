from datetime import datetime
import tkinter.filedialog as filedialog
import os

def export_cmx(edl_txt_path):
    """
    Exports entries from a QuickEDL TXT file to a CMX 3600-compatible EDL file
    with static markers. Prompts user to select the output file location.

    Parameters:
        edl_txt_path (str): Path to the original TXT file with EDL entries.
    """
    # Ask the user for the output file path
    cmx_output_path = filedialog.asksaveasfilename(
        defaultextension=".edl",
        filetypes=[("EDL Files", "*.edl"), ("All Files", "*.*")],
        title="Save CMX EDL File",
        initialfile="QuickEDL_CMX_export.edl"
    )
    
    # If the user cancels the save dialog, exit the function
    if not cmx_output_path:
        print("Export cancelled.")
        return

    try:
        # Open the TXT file with QuickEDL entries
        with open(edl_txt_path, 'r') as txt_file:
            entries = txt_file.readlines()
        
        # Open the output file for CMX-formatted EDL
        with open(cmx_output_path, 'w') as cmx_file:
            cmx_file.write("TITLE: QuickEDL Export\n\n")

            # Process each line in the TXT file and write it in CMX format
            entry_num = 1
            for line in entries:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines
                
                try:
                    # Extract timestamp and comment
                    timestamp, comment = line.split(" - ", 1)
                    cmx_file.write(f"{entry_num:03}  AX  V     C        {timestamp} {timestamp} {timestamp} {timestamp}\n")
                    cmx_file.write(f"* {comment.strip()}\n\n")
                    entry_num += 1
                except ValueError:
                    print(f"Skipping line due to format error: '{line}'")
        
        print(f"Export successful: {cmx_output_path}")

    except Exception as e:
        print(f"An error occurred during export: {e}")
