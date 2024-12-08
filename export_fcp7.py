import xml.etree.ElementTree as ET
from datetime import datetime
import os
from tkinter import messagebox, filedialog

# Frame rate constant for calculating frame timecodes
FRAME_RATE = 50

def convert_time_to_frames(time_str):
    # Convert time string (HH:MM:SS) to frames since 00:00:00.
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    return total_seconds * FRAME_RATE

###########################################
# Other method of parsing, currently unused
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
    try:
        messagebox.showinfo("Export", f"FCP7-XML exportiert nach {output_path}.")

    except RuntimeError:
        print("Messagebox failed: FCP7-Export successful.}")
###########################################

def export_to_xml_with_static(file_path):
    entries = []
    if not file_path:
        raise ValueError("No EDL file has been loaded.")

    # Read entries from the TXT file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Convert each entry in TXT to XML format and add to content
    for line in lines:
        # Check if the line has the expected delimiter
        if " - " in line:
            try:
                # Split into timestamp and text
                time_str, text = line.split(" - ", 1)
                time_str = time_str.strip()
                text = text.strip()

                # Ensure the timestamp matches the HH:MM:SS format
                time_obj = datetime.strptime(time_str, "%H:%M:%S")
                frames = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 50

                entry = {
                    "name": text,
                    "in": frames,
                    "out": frames + 50,  # Example, can be adjusted
                    "comment": ""
                }
                entries.append(entry)
                
            except ValueError:
                print(f"Skipping line due to formatting issue: {line.strip()}")
        else:
            print(f"Skipping line due to missing delimiter: {line.strip()}")

    # Define output XML file path and write the full content
    initial_dir = os.path.dirname(file_path)
    default_filename = "FCP7 Markers.xml"

    output_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        initialfile=default_filename,
        defaultextension=".xml",
        filetypes=[("XML files", "*.xml")]
    )

    with open(output_path, "w") as output_file:

        # Add prefix
        output_file.write("""
<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="4">
    <sequence id="sequence-1" TL.SQAudioVisibleBase="0" TL.SQVideoVisibleBase="0" TL.SQVisibleBaseTime="0" TL.SQAVDividerPosition="0.5" TL.SQHideShyTracks="0" TL.SQHeaderWidth="184" Monitor.ProgramZoomOut="0" Monitor.ProgramZoomIn="0" TL.SQTimePerPixel="0.73210623869801095" MZ.EditLine="36072439603200" MZ.Sequence.PreviewFrameSizeHeight="1080" MZ.Sequence.PreviewFrameSizeWidth="1920" MZ.Sequence.AudioTimeDisplayFormat="200" MZ.Sequence.PreviewRenderingClassID="1297106761" MZ.Sequence.PreviewRenderingPresetCodec="1297107278" MZ.Sequence.PreviewRenderingPresetPath="EncoderPresets/SequencePreview/795454d9-d3c2-429d-9474-923ab13b7018/I-Frame Only MPEG.epr" MZ.Sequence.PreviewUseMaxRenderQuality="false" MZ.Sequence.PreviewUseMaxBitDepth="false" MZ.Sequence.EditingModeGUID="795454d9-d3c2-429d-9474-923ab13b7018" MZ.Sequence.VideoTimeDisplayFormat="102" MZ.WorkOutPoint="0" MZ.WorkInPoint="0" explodedTracks="true">
        <uuid>e6d240fb-cb71-423a-89ab-9d68fd806b2e</uuid>
        <duration>0</duration>
        <rate>
            <timebase>50</timebase>
            <ntsc>FALSE</ntsc>
        </rate>
        <name>Sequence with Markers</name>
        <timecode>
            <rate>
                <timebase>50</timebase>
                <ntsc>FALSE</ntsc>
            </rate>
            <string>00;00;00;00</string>
            <frame>0</frame>
            <displayformat>DF</displayformat>
        </timecode>
        """
        )
        
        # Add entries
        for entry in entries:
            output_file.write(
                f"<marker>\n"
                f"    <comment>{entry['comment']}</comment>\n"
                f"    <name>{entry['name']}</name>\n"
                f"    <in>{entry['in']}</in>\n"
                f"    <out>{entry['out']}</out>\n"
                f"</marker>\n")
        # Add suffix
        output_file.write("""
	</sequence>
</xmeml>

        """
        )
    try:
        messagebox.showinfo("Export", f"FCP7-XML exportiert nach {output_path}.")

    except RuntimeError:
        print("Messagebox failed: FCP7-Export successful.}")
    print(f"XML export completed: {output_path}")
