# QuickEDL
# 2024-2025 / Eric Kirchheim (punkerschaf)

import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, RIGHT
from ttkbootstrap.dialogs import Messagebox

from datetime import datetime
from tkinter import filedialog, StringVar
from tkinter import END
from pathlib import Path
import logging

from about import show_about
from random_entry import random_entry
from export_jsx import JSXExportWindow
from utils import open_directory
import settings
from playlist import Playlist

# version number
version = "2.1"

class QuickEDLApp:
    def __init__(self, root):
        self.setup_logging()
        self.root = root
        self.root.title(f"QuickEDL {version}")
        self.root.geometry("400x700")
        self.style = ttk.Style("darkly")

        # File path for current EDL
        self.file_path = None
        self.current_dir = None
        self.last_entries = []
        self.settings_folder = None
        self.settings_folder_str = StringVar(value=str(self.settings_folder))

        # settings
        self.log_level = "DEBUG"
        self.funny = False
        self.default_dir = None
        self.delete_key = False

        # Hotkey status
        self.hotkeys_active = False
        self.entry_focused = False
        self.window_focused = True
        self.hotkey_status = None # init-Placeholder for label widget

        # Playlist
        self.playlist = Playlist()

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
        app_menu.add_command(label="About", command=lambda: show_about(self, version))
        app_menu.add_separator()
        app_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="App", menu=app_menu)

        edl_menu = ttk.Menu(menu_bar, tearoff=0)
        edl_menu.add_command(label="New EDL", command=self.create_new_file)
        edl_menu.add_command(label="Open EDL", command=self.load_file)
        edl_menu.add_separator()
        edl_menu.add_command(label="Export JSX", command=lambda: JSXExportWindow(self.root, self.file_path))
        menu_bar.add_cascade(label="EDL", menu=edl_menu)

        texts_menu = ttk.Menu(menu_bar, tearoff=0)
        texts_menu.add_command(label="Save texts", command=self.save_texts)
        texts_menu.add_command(label="Load texts", command=self.open_texts)
        texts_menu.add_command(label="Load default texts", command=self.load_default_texts)
        texts_menu.add_separator()
        texts_menu.add_command(label="Edit playlist", command=self.playlist.playlist_edit_window)
        menu_bar.add_cascade(label="Texts", menu=texts_menu)

        self.root.config(menu=menu_bar)

    def create_widgets(self):
        self.root.bind("<Return>", self.defocus_text)
        self.root.bind("<BackSpace>", self.handle_backspace)
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind_all("<FocusIn>", self.check_entry_focus)
        self.root.bind("<Button-1>", self.on_root_click)

        # File label
        self.file_labelframe = ttk.Labelframe(self.root, bootstyle="warning", text=" loaded File ")
        self.file_labelframe.grid(column=1, columnspan=6, row=1, padx=10, sticky="EW")
        self.file_label = ttk.Label(self.file_labelframe, text="No EDL file loaded.")
        self.file_label.pack(anchor="w", padx=5, pady=5)
        self.file_label.bind("<Double-Button-1>", lambda e:open_directory(self.file_path))

        # Time display
        self.time_label = ttk.Label(self.root, text="", font=("Courier New", 26))
        self.time_label.grid(column=1, columnspan=6, row=2)
        self.update_time()

        # Hotkey status label
        self.hotkey_status = ttk.Label(self.root, text="Hotkeys Active", font=("Courier New", 14), bootstyle="success")
        self.hotkey_status.grid(column=1, columnspan=6, row=3)

        # Text entry fields
        self.text_entries = []
        for i in range(9):
            frame = ttk.Frame(self.root)
            frame.grid(column=2, columnspan=5, row=i+4, padx=10, sticky="EW")

            entry = ttk.Entry(frame, width=30)
            entry.pack(side=LEFT, padx=10, pady=5)
            entry.bind("<Button-1>", self.on_entry_click, add="+")
            self.text_entries.append(entry)

            button = ttk.Button(frame, text=f"{i + 1}", command=lambda i=i: self.add_to_file(i), width=2)
            button.pack(side=RIGHT, pady=5)

        # Playlist
        playlist_frame = ttk.Frame(self.root)
        playlist_frame.grid(column=2, columnspan=5, row=13, padx=10, sticky="EW")

        playlist_label = ttk.Label(playlist_frame, 
                                   textvariable=self.playlist.playhead_text, 
                                   bootstyle="primary")
        playlist_label.grid(column=1, row=0, sticky="EW")
        playlist_frame.columnconfigure(1, weight=1)
        
        self.plst_dec_button = ttk.Button(playlist_frame, 
                                          text="<", 
                                          bootstyle="primary", 
                                          command= self.playlist.dec_playhead, 
                                          state="disabled")
        self.plst_dec_button.grid(column=2, row=0, sticky="E")
        playlist_frame.columnconfigure(2, weight=0)
        self.playlist.dec_able.trace_add("write", self.update_dec_button)

        self.plst_inc_button = ttk.Button(playlist_frame, text=">", 
                                          bootstyle="primary", 
                                          command= self.playlist.inc_playhead, 
                                          state="disabled")
        self.plst_inc_button.grid(column=3, row=0, sticky="E", padx=5)
        playlist_frame.columnconfigure(3, weight=0)
        self.playlist.inc_able.trace_add("write", self.update_inc_button)
 
        playlist_button = ttk.Button(playlist_frame, text="Plst", width=3, command= self.add_playlist_entry)
        playlist_button.grid(column=4, row=0, sticky="E")
        playlist_frame.columnconfigure(4, weight=0)

        # Special entries
        separator_button = ttk.Button(root, text="Separator (0)", command=self.add_separator)
        separator_button.grid(column=3, row= 14, padx=5, pady=5, sticky="E")

        popup_button = ttk.Button(root, text="Popup (Space)", command=self.add_with_popup)
        popup_button.grid(column=4, row= 14, padx=5, pady=5, sticky="E")

        delete_button = ttk.Button(root, text="Delete", bootstyle="danger-outline", command=self.delete_last_entry)
        delete_button.grid(column=5, row= 14, padx=5, pady=5, sticky="E")

        # Last entries display
        self.entries_labelframe = ttk.Labelframe(self.root, bootstyle="primary", text=" History ")
        self.entries_labelframe.grid(column=1, columnspan=6, row=16, sticky="NSEW", padx=10, pady=5)
        self.last_entries_text = ttk.StringVar(value="No entries yet.")
        last_entries_label = ttk.Label(self.entries_labelframe, textvariable=self.last_entries_text, justify=LEFT)
        last_entries_label.pack(pady=5, fill="both", expand=True)

        root.rowconfigure(16, weight=1)
        root.columnconfigure(1, weight=1, minsize=10)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(6, weight=0, minsize=10)


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
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    # Focus Control
    ###############

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

    def check_entry_focus(self, event):
        """
        Checks, if the focused widget is an entry field and handles the hotkey status.
        """
        if isinstance(event.widget, ttk.Entry):
            self.entry_focused = True
            self.update_hotkey_status()
        else:
            self.entry_focused = False
            self.update_hotkey_status()

    def defocus_text(self, event):
        if self.entry_focused:
            self.root.focus_set()
            self.entry_focused = False
            self.update_hotkey_status()

    def on_root_click(self, event):
        if not isinstance(event.widget, ttk.Entry) and not isinstance(event.widget, ttk.Button):
            self.root.focus_set()
            self.entry_focused = False
            self.update_hotkey_status()

    def on_entry_click(self, event):
        event.widget.focus_set()
        self.entry_focused = True
        self.update_hotkey_status()

    def set_entry_focus(self, focused):
        self.entry_focused = focused
        self.update_hotkey_status()

    def update_hotkey_status(self):
        if self.window_focused and not self.entry_focused:
            self.hotkeys_active = True
            self.hotkey_status.config(text="Hotkeys Active", bootstyle="success")
        else:
            self.hotkeys_active = False
            self.hotkey_status.config(text="Hotkeys Inactive", bootstyle="inverse-danger")
    
    # Others GUI functions
    def on_key_press(self, event):
        if self.root.focus_get() not in self.text_entries:
            key = event.char
            if key.isdigit():
                key_num = int(key)
                if key_num == 0:
                    self.add_separator()  # '0' separator
                elif 1 <= key_num <= 9:  # '1-9' 
                    self.add_to_file(key_num - 1)
                    self.flash_button(key_num - 1)
            elif event.keysym == "p":  # 'p' playlist entry
                self.add_playlist_entry()
            elif event.keysym == "space":  # 'space' popup entry
                self.add_with_popup()
    
    def flash_button(self, index):
        self.text_entries[index].config(bootstyle="danger")
        self.root.after(500, lambda: self.text_entries[index].config(bootstyle="default"))
    
    def update_dec_button(self, *args):
        if not self.playlist.dec_able.get():
            self.plst_dec_button.configure(state="disabled")
        else:
            self.plst_dec_button.configure(state="")
    
    def update_inc_button(self, *args):
        if not self.playlist.inc_able.get():
            self.plst_inc_button.configure(state="disabled")
        else:
            self.plst_inc_button.configure(state="")

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
            self.file_label.config(text=f"{self.file_path}")
            self.file_labelframe.config(bootstyle="success")
            with self.file_path.open('r') as file:
                lines = file.readlines()
                for line in lines:
                    self.update_last_entries(line)

    def save_texts(self):
        save_path = filedialog.asksaveasfilename(
            initialdir=self.current_dir,
            defaultextension=".txt",
            initialfile=f"TextFields_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if save_path:
            save_path = Path(save_path)
            save_path.write_text("\n".join(entry.get() for entry in self.text_entries) + "\n")

    def open_texts(self):
        load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")],
                                               initialdir=self.current_dir)
        self.import_texts(load_path)

    def import_texts(self, load_path):    
        if load_path:
            load_path = Path(load_path)
            lines = load_path.read_text().splitlines()
            for i, line in enumerate(lines[:9]):
                self.text_entries[i].delete(0, END)
                self.text_entries[i].insert(0, line.strip())
            logging.info(f"Importet texts from {load_path}")
    
    def load_settings(self):
        self.settings_folder = settings.get_settings_folder()
        self.settings_folder_str = StringVar(value=str(self.settings_folder))
        if self.settings_folder.exists():
            load_path = self.settings_folder / "texts.txt"
            if load_path.exists():
                self.import_texts(load_path)
                settings.load_yaml(self)
                logging.info(f"Imported texts and settings from {load_path}")
            else:
                return
        else:
            logging.info("No texts loaded.")
    
    def load_default_texts(self):
        if self.settings_folder.exists():
            load_path = self.settings_folder / "texts.txt"
            if load_path.exists():
                self.import_texts(load_path)
                logging.info(f"Imported texts and settings from {load_path}")
            else:
                Messagebox.show_error("Default text file doesn't exist.")
                logging.error("Default text file doesn't exist.")
                return
        else:
            Messagebox.show_error("Settingsfolder not found.")
            logging.error("Settingsfolder not found.")


# entries
####  #  #  ####  ###   ###   ####   ###
#     ## #   #    #  #   #    #     #
###   # ##   #    ####   #    ###   ####
#     # ##   #    # #    #    #        #
####  #  #   #    #  #  ###   ####  ###

    def add_to_file(self, index, *args):
        if self.hotkeys_active and self.file_path:
            text = self.text_entries[index].get()
            if not text and self.funny:
                text = random_entry(self)
            elif not text and not self.funny:
                text = f"Button {index +1}"
            entry = f"{datetime.now().strftime('%H:%M:%S')} - {text}"
            with Path(self.file_path).open('a') as file:
                file.write(entry + "\n")
            self.update_last_entries(entry)        
        else:
            self.entry_error()

    def add_with_popup(self):
        if self.hotkeys_active and self.file_path:
            timestamp = datetime.now().strftime("%H:%M:%S")
            entry = f"{timestamp} - "

            def get_input(event=None):
                text_input = input_var.get()
                popup.destroy()
                if text_input:
                    entry_popup = entry + text_input
                    with Path(self.file_path).open('a') as file:
                        file.write(entry_popup + "\n")
                    self.update_last_entries(entry_popup)

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

    def add_playlist_entry(self):
        if self.hotkeys_active and self.file_path:
            text = self.playlist.playlist_entry()
            entry = f"{datetime.now().strftime('%H:%M:%S')} - {text}"
            with Path(self.file_path).open('a') as file:
                file.write(entry + "\n")
            self.update_last_entries(entry)        
        else:
            self.entry_error()

    def handle_backspace(self, event):
        if event.widget not in self.text_entries and self.delete_key:
            self.delete_last_entry(self)

    def delete_last_entry(self, event):  
        if self.file_path and self.last_entries:
            with Path(self.file_path).open('r') as file:
                lines = file.readlines()
            if lines:
                lines = lines[:-1]
                with Path(self.file_path).open('w') as file:
                    file.writelines(lines)
            self.last_entries.pop()
            self.last_entries_text.set("\n".join(self.last_entries))
        else:
            self.entry_error()

    def add_separator(self):
        if self.hotkeys_active and self.file_path:
            separator = "-" * 20
            with open(self.file_path, 'a') as file:
                file.write(separator + "\n")
            self.update_last_entries(separator)        
        else:
            self.entry_error()

    def update_last_entries(self, new_entry):
        if new_entry.strip():  # Only add non-empty entries
            self.last_entries.append(new_entry.strip())
        if len(self.last_entries) > 5:
            self.last_entries.pop(0)
        self.last_entries_text.set("\n".join(self.last_entries))


### ERRORS ###
##############

    def entry_error(self):
        if not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")
        else:
            Messagebox.show_error("No EDL file has been created. Please create a file first.")


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
