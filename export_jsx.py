import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from pathlib import Path
import logging
import re

class JSXExportWindow:
    def __init__(self, root, file_path):
        self.root = root
        self.fps = 50
        self.timeline_start = "00:00:00" # HH:mm:ss
        self.timeline_offset = 0 # in seconds

        if file_path is not None:
            self.file_path = Path(file_path)
            self.get_edl_entries()
            self.create_window()
        else:
            Messagebox.show_error("No EDL file has been loaded.")

    def create_window(self):
        export_window = ttk.Toplevel(self)
        export_window.title("QuickEDL: Export for Premiere Pro")
        export_window.geometry("400x300")

        export_window.bind("<Button-1>", lambda event: event.widget.focus_set())

        # Grid
        export_window.columnconfigure(0, weight=1)
        export_window.columnconfigure(1, weight=1)

        # Widgets
        label = ttk.Label(export_window, text="Export settings for Premiere Pro")
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="n")

        fps_label = ttk.Label(export_window, text="Frames per second (FPS):")
        fps_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        fps_spinbox = ttk.Spinbox(export_window, from_=24, to=120, increment=1, textvariable=ttk.IntVar(value=self.fps), width=5)
        fps_spinbox.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        fps_spinbox.set(self.fps)
        fps_spinbox.bind("<<Increment>>", lambda e: update_fps())
        fps_spinbox.bind("<<Decrement>>", lambda e: update_fps())
        fps_spinbox.bind("<FocusOut>", lambda e: update_fps())

        timeline_label = ttk.Label(export_window, text="Start Timeline (HH:mm:ss):")
        timeline_label.grid(row=2, column=0, sticky="w")

        self.timeline_start_var = ttk.StringVar(value=self.timeline_start)
        timeline_entry = ttk.Entry(export_window, text="Timeline", textvariable=self.timeline_start_var, width=10)
        timeline_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        timeline_entry.bind("<FocusOut>", lambda e: update_timeline_start())

        generate_button = ttk.Button(export_window, text="Generate JSX", command=lambda: self.generate_jsx_script())
        generate_button.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        close_button = ttk.Button(export_window, text="Close", bootstyle="danger-outline", command=export_window.destroy)
        close_button.grid(row=4, column=0, padx=10, pady=10, sticky="se")

        def val_timeline_entry(*args):
            try:
                hours, minutes, seconds = map(int, self.timeline_start_var.get().split(":"))
                timeline_entry.config(bootstyle="success")
            except ValueError:
                timeline_entry.config(bootstyle="danger")

        def update_timeline_start():
            self.timeline_start = timeline_entry.get()
            if re.match(r"^\d{2}:\d{2}:\d{2}$", self.timeline_start):
                self.calc_timeline_offset()
            else:
                logging.error("Invalid time format for timeline start.")
                Messagebox.show_error("Invalid time format for timeline start.")

        def update_fps():
            try:
                self.fps = int(fps_spinbox.get())
                logging.info(f"FPS updated to {self.fps}")
            except ValueError:
                logging.error("Invalid FPS value entered.")

    def calc_timeline_offset(self):
        try:
            hours, minutes, seconds = map(int, self.timeline_start.split(":"))
            self.timeline_offset = hours * 3600 + minutes * 60 + seconds
            print(f"timeline offset: {self.timeline_offset} frames.")
        except ValueError: 
            
            logging.error("calc_timeline_offset failed")

    def get_edl_entries(self):
        try:
            with self.file_path.open('r') as file:
                self.entries = [line.strip() for line in file.readlines() if " - " in line]
                self.entries_count = len(self.entries)
            logging.info(f"{self.entries_count} EDL entries loaded from {self.file_path}")
        except Exception as e:
            logging.error(f"An error occurred while reading the EDL file: {e}", exc_info=True)
    
    def generate_jsx_script(self):
        self.calc_timeline_offset()
        try:
            output_path = self.file_path.parent / "output_script.jsx"
            print(output_path)
            jsx_content = """
var project = app.project;
var sequence = project.activeSequence;
if (sequence) {
    var markers = sequence.markers;
    var fps = 50; // Frames per second
"""
            for entry in self.entries:
                time_str, text = entry.split(" - ", 1)
                hours, minutes, seconds = map(int, time_str.split(":"))
                marker_seconds = (hours * 3600 + minutes * 60 + seconds) - self.timeline_offset
                jsx_content += f"""
    var newMarker = markers.createMarker({marker_seconds});
    newMarker.name = "{text}";
"""
                print(f"entry converted: {text} at {marker_seconds} seconds.")
            jsx_content += """
} else {
    alert("No active sequence found.");
}
"""
            with open(output_path, 'w') as jsx_file:
                jsx_file.write(jsx_content)
            logging.info(f"JSX script generated at {output_path}")
            print(f"JSX generated at{output_path}")
            
        except Exception as e:
            logging.error(f"An error occurred while generating the JSX script: {e}", exc_info=True)
"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    edl_file = "path/to/your/edl_file.txt"
    output_jsx = "path/to/your/output_script.jsx"
    exporter = jsx_export(edl_file)
    exporter.open_export_window()
    exporter.generate_jsx_script(output_jsx)
    print(f"JSX script generated at {output_jsx}")
"""