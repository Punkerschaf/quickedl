# QuickEDL
# 2024-2025 / Eric Kirchheim (punkerschaf)

import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, RIGHT
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification

from datetime import datetime
from tkinter import filedialog, StringVar
from tkinter import END
from pathlib import Path
import logging
import sys

# import internals
from about import show_about
from random_entry import random_markerlabel
from export_jsx import JSXExportWindow
from utils import open_directory
import settings
from playlist import Playlist
from markerlabel import save_markerlabel
from projects.project import Project
from projects.newproject import show_new_project_window
from version import VERSION

# version number
version = VERSION

class QuickEDLApp:
    def __init__(self, root):
        self.setup_logging()
        self.root = root
        self.root.title(f"QuickEDL {version}")
        self.root.geometry("400x700")
        self.style = ttk.Style("darkly")

        # Legacy file path for standalone EDL files (not part of project)
        self.file_path = None
        self.current_dir = None
        self.last_markers = []
        self.settings_folder = None
        self.settings_folder_str = StringVar(value=str(self.settings_folder))

        # settings
        self.log_level = "DEBUG"
        self.funny = False
        self.default_dir = None
        self.delete_key = False

        # Hotkey status
        self.hotkeys_active = True
        self.entry_focused = False
        self.window_focused = True
        self.hotkey_status = None # init-Placeholder for label widget

        # Project
        self.project = Project(update_callback=self.update_project_display)

        # Playlist
        self.playlist = Playlist(project=self.project)

        # create window
        self.create_menu()
        self.create_widgets()
        self.check_window_focus()

    def setup_logging(self):
        home_dir = Path.home()
        log_file = home_dir / "quickedl.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, mode='w'),
                logging.StreamHandler()
            ])
        logging.info(f"Logging initialized at {log_file}.")

    def load_project_history(self):
        """
        Loads the history from the current project's EDL file.
        """
        if self.project.project_edl_file and Path(self.project.project_edl_file).exists():
            # Clear existing history
            self.last_markers.clear()
            
            try:
                with Path(self.project.project_edl_file).open('r', encoding='utf-8') as file:
                    lines = file.readlines()
                    # Get the last 5 lines that are not empty
                    non_empty_lines = [line.strip() for line in lines if line.strip()]
                    recent_lines = non_empty_lines[-5:] if len(non_empty_lines) >= 5 else non_empty_lines
                    
                    # Add them to history without using update_last_markers to avoid duplication
                    self.last_markers.extend(recent_lines)
                    self.last_markers_text.set("\n".join(self.last_markers))
                    
                logging.info(f"Loaded {len(recent_lines)} markers from project EDL file: {self.project.project_edl_file}")
            except Exception as e:
                logging.error(f"Error loading project history: {e}")
        else:
            # Clear history if no valid project file
            self.last_markers.clear()
            self.last_markers_text.set("No markers yet.")

    def update_project_display(self):
        """
        Updates the project display based on the current project state.
        """
        if self.project.project_isvalid and self.project.project_name:
            self.file_label.config(text=f"Project: {self.project.project_name}")
            self.file_labelframe.config(bootstyle="success")
            self.load_project_history()
        else:
            self.file_label.config(text="No project loaded.")
            self.file_labelframe.config(bootstyle="warning")

# GUI
####  #  #  ###
#     #  #   #
####  #  #   #
#  #  #  #   #
 ###  ####  ###

    def create_menu(self):
        menu_bar = ttk.Menu(self.root)

        app_menu = ttk.Menu(menu_bar, tearoff=0)
        app_menu.add_command(label="Settings", command=lambda: settings.show_settings_window(self))

        if sys.platform == "darwin":
            self.root.createcommand("tkAboutDialog", lambda: show_about(self, version))
        else:
            app_menu.add_command(label="About", command=lambda: show_about(self, version))

        app_menu.add_separator()
        app_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="App", menu=app_menu)
        
        project_menu = ttk.Menu(menu_bar, tearoff=0)
        project_menu.add_command(label="New Project", command=lambda: show_new_project_window(self.root, self.project, self))
        project_menu.add_command(label="Load Project", command=self.project.load_project_dialog)
        project_menu.add_command(label="Save Labels to Project", command= lambda: save_markerlabel(self, save_path=self.project.project_markerlabel_file))
        menu_bar.add_cascade(label="Project", menu=project_menu)

        edl_menu = ttk.Menu(menu_bar, tearoff=0)
        edl_menu.add_command(label="New EDL", command=self.create_new_file)
        edl_menu.add_command(label="Open EDL", command=self.load_file)
        edl_menu.add_separator()
        edl_menu.add_command(label="Export JSX", command=lambda: JSXExportWindow(self.root, self.project.project_edl_file))
        menu_bar.add_cascade(label="EDL", menu=edl_menu)

        texts_menu = ttk.Menu(menu_bar, tearoff=0)
        texts_menu.add_command(label="Save markerlabels", command=self.save_markerlabels)
        texts_menu.add_command(label="Load markerlabels", command=self.open_markerlabels)
        texts_menu.add_command(label="Load default markerlabels", command=self.load_default_markerlabels)
        texts_menu.add_separator()
        texts_menu.add_command(label="Edit playlist", command=self.playlist.playlist_edit_window)
        menu_bar.add_cascade(label="Markerlabels", menu=texts_menu)

        self.root.config(menu=menu_bar)

    def create_widgets(self):
        self.root.bind("<Button-1>", self.defocus_text)
        self.root.bind("<Return>", self.defocus_text)
        self.root.bind("<BackSpace>", self.handle_backspace)
        self.root.bind("<KeyPress>", self.on_key_press)

        # File label
        self.file_labelframe = ttk.Labelframe(self.root, bootstyle="warning", text=" Project ")
        self.file_labelframe.grid(column=1, columnspan=6, row=1, padx=10, sticky="EW")
        self.file_label = ttk.Label(self.file_labelframe, text="No project loaded.")
        self.file_label.pack(anchor="w", padx=5, pady=5)
        self.file_label.bind("<Double-Button-1>", lambda e:open_directory(self.project.project_edl_file))

        # Time display
        self.time_label = ttk.Label(self.root, text="", font=("Courier New", 26))
        self.time_label.grid(column=2, columnspan=3, row=2)
        self.update_time()

        # Hotkey status label
        self.hotkey_status = ttk.Label(self.root, text="Hotkeys Active", font=("Courier New", 14), bootstyle="success")
        self.hotkey_status.grid(column=2, columnspan=3, row=3)

        # Text entry fields
        self.markerlabel_entries = []
        for i in range(9):
            frame = ttk.Frame(self.root)
            frame.grid(column=2, columnspan=5, row=i+4, padx=10, sticky="EW")

            entry = ttk.Entry(frame, width=30)
            entry.pack(side=LEFT, padx=10, pady=5)
            self.markerlabel_entries.append(entry)

            button = ttk.Button(frame, text=f"{i + 1}", command=lambda i=i: self.add_to_file(i), width=2)
            button.pack(side=RIGHT, pady=5)

        self.bind_markerlabel_entries()

        # Playlist
        playlist_frame = ttk.Frame(self.root)
        playlist_frame.grid(column=2, columnspan=5, row=13, padx=10, sticky="EW")

        playlist_label = ttk.Label(playlist_frame, 
                                   textvariable=self.playlist.playhead_text, 
                                   bootstyle="primary")
        playlist_label.grid(column=1, row=0, sticky="EW")
        playlist_frame.columnconfigure(1, weight=1)
        
        self.plst_dec_button = ttk.Button(playlist_frame, text="<", bootstyle="primary", command= self.playlist.dec_playhead)
        self.plst_dec_button.grid(column=2, row=0, sticky="E")
        playlist_frame.columnconfigure(2, weight=0)

        self.plst_inc_button = ttk.Button(playlist_frame, text=">", bootstyle="primary", command= self.playlist.inc_playhead)
        self.plst_inc_button.grid(column=3, row=0, sticky="E", padx=5)
        playlist_frame.columnconfigure(3, weight=0)
 
        playlist_button = ttk.Button(playlist_frame, text="Plst", width=3, command=lambda event: self.add_to_file(self.playlist.playhead_stringvar))
        playlist_button.grid(column=4, row=0, sticky="E")
        playlist_frame.columnconfigure(4, weight=0)

        # Special markerlabel entries
        separator_button = ttk.Button(root, text="Separator (0)", command=self.add_separator)
        separator_button.grid(column=3, row= 14, padx=5, pady=5, sticky="E")

        popup_button = ttk.Button(root, text="Popup (Space)", command=self.add_with_popup)
        popup_button.grid(column=4, row= 14, padx=5, pady=5, sticky="E")

        delete_button = ttk.Button(root, text="Delete", bootstyle="danger-outline", command=self.delete_last_marker)
        delete_button.grid(column=5, row= 14, padx=5, pady=5, sticky="E")

        # Last markers display
        self.markers_labelframe = ttk.Labelframe(self.root, bootstyle="primary", text=" History ")
        self.markers_labelframe.grid(column=1, columnspan=6, row=16, sticky="NSEW", padx=10, pady=5)
        self.last_markers_text = ttk.StringVar(value="No markers yet.")
        last_markers_label = ttk.Label(self.markers_labelframe, textvariable=self.last_markers_text, justify=LEFT)
        last_markers_label.pack(pady=5, fill="both", expand=True)

        root.rowconfigure(16, weight=1)
        root.columnconfigure(1, weight=1, minsize=10)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(6, weight=0, minsize=10)

    def bind_markerlabel_entries(self):
        for entry in self.markerlabel_entries:
            entry.bind("<FocusIn>", lambda e: self.set_entry_focus(True))
            entry.bind("<FocusOut>", lambda e: self.set_entry_focus(False))

#####################
### GUI FUNCTIONS ###
#####################

    def adjust_window_height(self):
        """
        Adjust the height of the root window to fit all widgets.
        """
        self.root.update_idletasks()  # Update "requested size" from geometry manager
        height = self.root.winfo_reqheight()
        self.root.geometry(f"400x{height}")

    def check_window_focus(self):
        """
        Check if the window is focused and update hotkey status.
        """
        try:
            focused_widget = self.root.focus_displayof()
            widget_name = str(focused_widget) if focused_widget else ""
            if widget_name and "#menu" not in widget_name:
                self.window_focused = True
            else:
                self.window_focused = False
        except KeyError:
            self.window_focused = False
        self.update_hotkey_status()
        self.root.after(100, self.check_window_focus)
    
    def defocus_text(self, event):
        # Check if click is in root
        if event.type == "2":  # KeyPress event
            if self.window_focused and self.entry_focused:
                self.root.focus_set()
        else:
            if event.widget not in self.markerlabel_entries:
                self.root.focus_set()
            else:
                event.widget.focus_set()

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def set_entry_focus(self, focused):
    # Set the entry focus status and update hotkey status.
        self.entry_focused = focused
        self.update_hotkey_status()

    def update_hotkey_status(self):
    # Update the hotkey status based on window and entry focus.
        if self.window_focused and not self.entry_focused:
            self.hotkeys_active = True
            self.hotkey_status.config(text="Hotkeys Active", bootstyle="success")
        else:
            self.hotkeys_active = False
            self.hotkey_status.config(text="Hotkeys Inactive", bootstyle="inverse-danger")
    
    def on_key_press(self, event):
    # Check if any text field has focus
        if self.root.focus_get() not in self.markerlabel_entries:
            key = event.char
            if key.isdigit():
                key_num = int(key)
                if key_num == 0:
                    self.add_separator()  # Separator for key '0'
                elif 1 <= key_num <= 9:
                    self.add_to_file(key_num - 1)  # Corresponding button for keys 1-9
                    self.flash_button(key_num - 1)
            elif event.keysym == "space":
                self.add_with_popup()  # Trigger the pop-up entry for spacebar
    
    def flash_button(self, index):
        self.markerlabel_entries[index].config(bootstyle="danger")
        self.root.after(500, lambda: self.markerlabel_entries[index].config(bootstyle="default"))
    
    def toast(self, message): #TODO Remove Toast and Toast call at start
        toast = ToastNotification(
            title="QuickEDL",
            message=message,
            duration=3000,
            bootstyle="primary",
            icon=""
        )
        toast.show_toast()
    
    def update_playlist_selector(self, lenght, *args):
        self.playlist_selector.configure(to=lenght)

#####################
### APP FUNCTIONS ###
#####################

# file handling
####  ###   #     ####
#      #    #     #
###    #    #     ###
#      #    #     #
#     ###   ####  ####

    def create_new_file(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"EDL_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                filetypes=[("Text files", "*.txt")])
            if file_path:
                self.file_path = Path(file_path)
                self.current_dir = self.file_path.parent
                with self.file_path.open('w') as file:
                    file.write("File created on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                # Note: This creates a standalone EDL file, not a project
                self.file_label.config(text=f"CREATED: {self.file_path}")
                self.file_labelframe.config(bootstyle="success")
                logging.info(f"New file created: {self.file_path}")
        except Exception as e:
            logging.error(f"An error occurred while creating a new file: {e}", exc_info=True)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_path = Path(file_path)
            self.current_dir = self.file_path.parent
            # Note: This loads a standalone EDL file, not a project
            self.file_label.config(text=f"{self.file_path}")
            self.file_labelframe.config(bootstyle="success")
            
            # Load history from file
            self.last_markers.clear()
            with self.file_path.open('r') as file:
                lines = file.readlines()
                # Get the last 5 lines that are not empty
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                recent_lines = non_empty_lines[-5:] if len(non_empty_lines) >= 5 else non_empty_lines
                self.last_markers.extend(recent_lines)
                self.last_markers_text.set("\n".join(self.last_markers))

    def save_markerlabels(self):
        save_path = filedialog.asksaveasfilename(
            initialdir=self.current_dir,
            defaultextension=".txt",
            initialfile=f"Markerlabels_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if save_path:
            save_path = Path(save_path)
            save_path.write_text("\n".join(entry.get() for entry in self.markerlabel_entries) + "\n")

    def open_markerlabels(self):
        load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")],
                                               initialdir=self.current_dir)
        self.import_markerlabels(load_path)

    def import_markerlabels(self, load_path):    
        if load_path:
            load_path = Path(load_path)
            lines = load_path.read_text().splitlines()
            for i, line in enumerate(lines[:9]):
                self.markerlabel_entries[i].delete(0, END)
                self.markerlabel_entries[i].insert(0, line.strip())
            logging.info(f"Imported markerlabels from {load_path}")
    
    def load_settings(self):
        self.settings_folder = settings.get_settings_folder()
        self.settings_folder_str = StringVar(value=str(self.settings_folder))
        if self.settings_folder.exists():
            load_path = self.settings_folder / "texts.txt"
            if load_path.exists():
                self.import_markerlabels(load_path)
                settings.load_yaml(self)
                self.toast("Found and loaded settings.")
                logging.info(f"Imported markerlabels and settings from {load_path}")
            else:
                return
        else:
            logging.info("No markerlabels loaded.")
    
    def load_default_markerlabels(self):
        if self.settings_folder.exists():
            load_path = self.settings_folder / "texts.txt"
            if load_path.exists():
                self.import_markerlabels(load_path)
                logging.info(f"Imported markerlabels and settings from {load_path}")
            else:
                Messagebox.show_error("Default markerlabel file doesn't exist.")
                logging.error("Default markerlabel file doesn't exist.")
                return
        else:
            Messagebox.show_error("Settingsfolder not found.")
            logging.error("Settingsfolder not found.")


# markers
####  #  #  ####  ###   ###   ####   ###
#     ## #   #    #  #   #    #     #
###   # ##   #    ####   #    ###   ####
#     # ##   #    # #    #    #        #
####  #  #   #    #  #  ###   ####  ###

    def add_to_file(self, index, *args):
        if self.hotkeys_active and self.project.project_edl_file:
            text = self.markerlabel_entries[index].get()
            if not text and self.funny:
                text = random_markerlabel(self)
            elif not text and not self.funny:
                text = f"Button {index +1}"
            marker = f"{datetime.now().strftime('%H:%M:%S')} - {text}"
            with Path(self.project.project_edl_file).open('a') as file:
                file.write(marker + "\n")
            self.update_last_markers(marker)        
        else:
            self.entry_error()

    def add_with_popup(self):
        if self.hotkeys_active and self.project.project_edl_file:
            timestamp = datetime.now().strftime("%H:%M:%S")
            marker = f"{timestamp} - "

            def get_input(event=None):
                text_input = input_var.get()
                popup.destroy()
                if text_input:
                    marker_popup = marker + text_input
                    with Path(self.project.project_edl_file).open('a') as file:
                        file.write(marker_popup + "\n")
                    self.update_last_markers(marker_popup)

            def cancel_popup(event = None):
                popup.destroy()
            
            popup = ttk.Toplevel(self.root)
            popup.title(f"Text for {timestamp}")
            popup.geometry("400x150")
            popup.resizable(False, False)
            popup.bind("<Escape>", cancel_popup)
            popup.bind("<Return>", get_input)

            input_var = ttk.StringVar()
            input_entry = ttk.Entry(popup, textvariable=input_var, width=50)
            input_entry.pack(pady=5)

            buttonframe = ttk.Frame(popup)
            buttonframe.pack(pady=10)
            cancel_button = ttk.Button(buttonframe, bootstyle="danger", text="Cancel", command=cancel_popup)
            cancel_button.pack(side=LEFT, padx=10, pady=10)
            submit_button = ttk.Button(buttonframe, bootstyle="success", text="Save", command=get_input)
            submit_button.pack(side=RIGHT, padx=10, pady=10)

            input_entry.focus()
            popup.transient(self.root)
            self.root.wait_window(popup)
        
        else:
            self.entry_error()

    def handle_backspace(self, event):
        if event.widget not in self.markerlabel_entries and self.delete_key:
            self.delete_last_marker(self)

    def delete_last_marker(self, **kwargs):  
        if self.project.project_edl_file and self.last_markers:
            # Read all lines from the file
            with Path(self.project.project_edl_file).open('r') as file:
                lines = file.readlines()
            # Remove the last line
            if lines:
                lines = lines[:-1]
                # Write the remaining lines back to the file
                with Path(self.project.project_edl_file).open('w') as file:
                    file.writelines(lines)            
            # Update last_markers list and label
            self.last_markers.pop()
            self.last_markers_text.set("\n".join(self.last_markers))
        else:
            self.entry_error()

    def add_separator(self):
        if self.hotkeys_active and self.project.project_edl_file:
            separator = "-" * 20
            with open(self.project.project_edl_file, 'a') as file:
                file.write(separator + "\n")
            self.update_last_markers(separator)        
        else:
            self.entry_error()

    def update_last_markers(self, new_marker):
        if new_marker.strip():  # Only add non-empty markers
            self.last_markers.append(new_marker.strip())
        if len(self.last_markers) > 5:
            self.last_markers.pop(0)
        self.last_markers_text.set("\n".join(self.last_markers))


### EXPORT ###
##############

    def export_cmx(self): #XXX
        # Placeholder for CMX export
        Messagebox.show_info("Export CMX functionality is not implemented yet.")

    def export_fcp7(self): #XXX
        # Placeholder for FCP7 export
        Messagebox.show_info("Export FCP7 XML functionality is not implemented yet.")

### ERRORS ###
##############

    def entry_error(self):
        if not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")
        else:
            Messagebox.show_error("No project loaded. Please create or load a project first.")


# MAIN APP CALL
#   #   ##   ###   #  #
## ##  #  #   #    ## #
# # #  ####   #    # ##
#   #  #  #  ###   #  #

if __name__ == "__main__":
    try:
        root = ttk.Window(themename="darkly")
        app = QuickEDLApp(root)
        app.load_settings()
        root.mainloop()
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise
