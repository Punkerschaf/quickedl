import xml.etree.ElementTree as ET
from datetime import datetime

# Frame rate constant for calculating frame timecodes
FRAME_RATE = 50

def convert_time_to_frames(time_str):
    # Convert time string (HH:MM:SS) to frames since 00:00:00.
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    return total_seconds * FRAME_RATE

def export_xml(file_path, output_path):
    # Calculate frame conversion factor for 50 fps
    frames_per_second = 50

    # Initialize the root of the XML tree and static elements
    root = ET.Element("root")
    static_element = ET.SubElement(root, "staticContent")
    static_element.text = "This is additional static content."

    # Read and parse each entry from the TXT file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if " - " in line:
                # Split each entry into text and time
                entry_text, time_str = line.strip().split(" - ")
                hours, minutes, seconds = map(int, time_str.split(":"))
                
                # Calculate frame-based timecodes (in and out)
                frame_start = (hours * 3600 + minutes * 60 + seconds) * frames_per_second
                frame_end = frame_start + 50  # Example duration of 1 second (50 frames)

                # Construct the marker element for each entry
                marker = ET.SubElement(root, "marker")
                ET.SubElement(marker, "comment").text = ""  # Empty comment
                ET.SubElement(marker, "name").text = entry_text
                ET.SubElement(marker, "in").text = str(frame_start)
                ET.SubElement(marker, "out").text = str(frame_end)

    # Write the XML structure to the output file
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    print(f"XML export completed and saved to {output_path}")