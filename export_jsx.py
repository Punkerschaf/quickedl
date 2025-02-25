import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.validation import add_regex_validation
from pathlib import Path
import logging
import re

from utils import open_directory
from confetti import show_confetti

class JSXExportWindow:
    def __init__(self, root, file_path):
        self.root = root
        self.timeline_start = "00:00:00" # HH:mm:ss
        self.timeline_offset = 0 # in seconds
        self.output_name = "output_script"
        self.done = False

        if file_path is not None:
            self.file_path = Path(file_path)
            self.get_edl_entries()
            self.create_window()
            logging.debug("JSXExportWindow init DONE.")
        else:
            Messagebox.show_error("No EDL file has been loaded.")

    def create_window(self):
        self.export_window = ttk.Toplevel(self)
        self.export_window.title("QuickEDL: Export for Premiere Pro")
        self.export_window.geometry("400x250")

        self.export_window.bind("<Button-1>", lambda event: event.widget.focus_set())

        # Grid
        self.export_window.columnconfigure(0, weight=1)
        self.export_window.columnconfigure(1, weight=1)

        # Widgets
        label = ttk.Label(self.export_window, text="Export settings for Premiere Pro")
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="n")

        ## FILE NAME
        name_label = ttk.Label(self.export_window, text="Filename:", anchor="e")
        name_label.grid(row=1, column=0,padx=5, pady=5,sticky="e")

        self.name_entry_var = ttk.StringVar(value=self.output_name)
        name_entry = ttk.Entry(self.export_window, textvariable=self.name_entry_var, width=15)
        name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        name_entry.bind("<Return>", lambda event: update_output_name())
        name_entry.bind("<FocusOut>", lambda event: update_output_name())

        ## TIMELINE START
        timeline_label = ttk.Label(self.export_window, text="Start Timeline (HH:mm:ss):", anchor="e")
        timeline_label.grid(row=2, column=0, sticky="e")

        self.timeline_start_var = ttk.StringVar(value=self.timeline_start)
        timeline_entry = ttk.Entry(self.export_window, text="Timeline", textvariable=self.timeline_start_var, width=10, bootstyle="success")
        timeline_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        add_regex_validation(timeline_entry, r'^\d{2}:\d{2}:\d{2}$', when='focus')
        timeline_entry.bind("<Return>", lambda event: self.export_window.focus_set())
        timeline_entry.bind("<FocusOut>", lambda event: update_timeline_start())

        ToolTip(timeline_entry, delay=500, text="""
Timecode start of your sequence. While markers are created in seconds relativ to this point, this is a bit of important.
This function is dumb as f***. Please enter as HH:mm:ss
""")

        ## BUTTONS
        close_button = ttk.Button(self.export_window, text="Close", bootstyle="danger-outline", command=self.export_window.destroy)
        close_button.grid(row=4, column=0, padx=10, pady=10, sticky="s")

        self.generate_button = ttk.Button(self.export_window, text="Generate JSX", command=lambda: self.generate_jsx_script())
        self.generate_button.grid(row=4, column=1, padx=10, pady=10, sticky="s")

        def update_timeline_start():
            self.timeline_start = timeline_entry.get()
            if re.match(r"^\d{2}:\d{2}:\d{2}$", self.timeline_start):
                self.calc_timeline_offset()
            else:
                logging.error("Invalid time format for timeline start.")
        
        def update_output_name():
            self.output_name = name_entry.get()

    def calc_timeline_offset(self):
        try:
            hours, minutes, seconds = map(int, self.timeline_start.split(":"))
            self.timeline_offset = hours * 3600 + minutes * 60 + seconds
            logging.info(f"timeline offset: {self.timeline_offset} frames.")
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
        if not self.done:
            try:
                self.output_path = self.file_path.parent / f"{self.output_name}.jsx"
                logging.debug(f"Generating JSX at{self.output_path}.")
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
                    logging.debug(f"entry converted: {text} at {marker_seconds} seconds.")
                jsx_content += """
} else {
    alert("No active sequence found.");
}
"""
                with open(self.output_path, 'w') as jsx_file:
                    jsx_file.write(jsx_content)
                logging.info(f"JSX script generated at {self.output_path}")
                self.export_success()
                    
            except Exception as e:
                logging.error(f"An error occurred while generating the JSX script: {e}", exc_info=True) 

    def export_success(self):
        self.generate_button.config(bootstyle="success-outline", text="Done.", command=None)
        self.done = True
        try:
            show_confetti(window=self.export_window)
        except Exception:
            logging.error("Confetti gun is empty.", exc_info=True)  
        self.export_window.after(1000, lambda: open_directory(self.output_path))
