"""
QuickEDL
2024-2025 / Eric Kirchheim (punkerschaf)

   ____        _      _      ______ _____  _      
  / __ \      (_)    | |    |  ____|  __ \| |     
 | |  | |_   _ _  ___| | __ | |__  | |  | | |     
 | |  | | | | | |/ __| |/ / |  __| | |  | | |     
 | |__| | |_| | | (__|   <  | |____| |__| | |____ 
  \___\_\\__,_|_|\___|_|\_\ |______|_____/|______|                                                

"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, RIGHT
from ttkbootstrap.dialogs import Messagebox

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
from settings import SettingsManager, show_settings_window
from settings.recent import RecentProjectsManager, RecentProjectsMenu
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

        # Initialize settings manager
        self.settings_manager = SettingsManager()

        # Auto-save timer
        self.auto_save_timer = None

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
        self.project = Project(
            update_callback=self.on_project_update,
            settings_manager=self.settings_manager
        )

        # Playlist
        self.playlist = Playlist(project=self.project)

        # Recent Projects Manager
        max_recent = self.settings_manager.get_setting('max_recent', 5)
        self.recent_manager = RecentProjectsManager(self.settings_manager, max_recent)
        self.recent_menu = None  # Will be initialized in create_menu

        # create window
        self.create_menu()
        self.create_widgets()
        self.check_window_focus()
        
        # Setup auto-save after everything is initialized
        self.setup_auto_save()

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

    # AUTO SAVE FUNCTIONS
    def setup_auto_save(self):
        """Sets up the auto-save functionality based on settings."""
        interval = self.settings_manager.get_setting('auto_save_interval', 300)
        if interval > 0:
            self.schedule_auto_save(interval)
            logging.info(f"Auto-save enabled with interval: {interval} seconds")
        else:
            logging.info("Auto-save disabled")

    def schedule_auto_save(self, interval_seconds):
        """Schedules the next auto-save."""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        # Schedule auto-save in milliseconds
        self.auto_save_timer = self.root.after(interval_seconds * 1000, self.perform_auto_save)

    def perform_auto_save(self):
        """Performs auto-save if conditions are met."""
        try:
            # Only auto-save if we have a project with markers
            if (self.project.project_isvalid and 
                self.project.project_markerlabel_file and 
                self.last_markers):
                
                # Save current markerlabels to project
                self.auto_save_markerlabels()
                logging.debug("Auto-save: Markerlabels saved to project")
            
            # Reschedule next auto-save
            interval = self.settings_manager.get_setting('auto_save_interval', 300)
            if interval > 0:
                self.schedule_auto_save(interval)
                
        except Exception as e:
            logging.error(f"Auto-save failed: {e}")
            # Still reschedule to try again later
            interval = self.settings_manager.get_setting('auto_save_interval', 300)
            if interval > 0:
                self.schedule_auto_save(interval)

#  ██████  ██    ██ ██ 
# ██       ██    ██ ██ 
# ██   ███ ██    ██ ██ 
# ██    ██ ██    ██ ██ 
#  ██████   ██████  ██ 
#                      
#                      
    def create_menu(self):
        menu_bar = ttk.Menu(self.root)

        app_menu = ttk.Menu(menu_bar, tearoff=0)
        app_menu.add_command(label="Settings", command=lambda: show_settings_window(self))

        if sys.platform == "darwin":
            self.root.createcommand("tkAboutDialog", lambda: show_about(self, version))
        else:
            app_menu.add_command(label="About", command=lambda: show_about(self, version))

        app_menu.add_separator()
        app_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="App", menu=app_menu)
        
        # Store reference to project menu for dynamic updates
        self.project_menu = ttk.Menu(menu_bar, tearoff=0)
        self.project_menu.add_command(label="New Project", command=lambda: show_new_project_window(self.root, self.project, self))
        self.project_menu.add_command(label="Load Project", command=self.project.load_project_dialog)
        self.project_menu.add_command(label="Save Labels to Project", command= lambda: save_markerlabel(self, save_path=self.project.project_markerlabel_file))
        
        # Initialize Recent Projects Menu
        self.recent_menu = RecentProjectsMenu(
            self.project_menu, 
            self.recent_manager, 
            self._load_recent_project
        )
        self.recent_menu.create_submenu()
        
        menu_bar.add_cascade(label="Project", menu=self.project_menu)

        edl_menu = ttk.Menu(menu_bar, tearoff=0)
        edl_menu.add_command(label="New EDL", command=self.create_new_file)
        edl_menu.add_command(label="Open EDL", command=self.load_file)
        edl_menu.add_separator()
        edl_menu.add_command(label="Export JSX", command=lambda: JSXExportWindow(self.root, self.project.project_edl_file if self.project.project_edl_file else self.file_path))
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
        # Bind events only to the root window, not all widgets
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<BackSpace>", self.handle_backspace)
        # Only bind click events to specific areas where defocusing makes sense
        self.root.bind("<Button-1>", self.defocus_text)

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
 
        playlist_button = ttk.Button(playlist_frame, text="Plst", width=3, command=self.add_playlist_to_file)
        playlist_button.grid(column=4, row=0, sticky="E")
        playlist_frame.columnconfigure(4, weight=0)

        # Special markerlabel entries
        separator_button = ttk.Button(self.root, text="Separator (0)", command=self.add_separator)
        separator_button.grid(column=3, row= 14, padx=5, pady=5, sticky="E")

        popup_button = ttk.Button(self.root, text="Popup (Space)", command=self.add_with_popup)
        popup_button.grid(column=4, row= 14, padx=5, pady=5, sticky="E")

        delete_button = ttk.Button(self.root, text="Delete", bootstyle="danger-outline", command=self.delete_last_marker)
        delete_button.grid(column=5, row= 14, padx=5, pady=5, sticky="E")

        # Last markers display
        self.markers_labelframe = ttk.Labelframe(self.root, bootstyle="primary", text=" History ")
        self.markers_labelframe.grid(column=1, columnspan=6, row=16, sticky="NSEW", padx=10, pady=5)
        self.last_markers_text = ttk.StringVar(value="No markers yet.")
        last_markers_label = ttk.Label(self.markers_labelframe, textvariable=self.last_markers_text, justify=LEFT)
        last_markers_label.pack(pady=5, fill="both", expand=True)

        self.root.rowconfigure(16, weight=1)
        self.root.columnconfigure(1, weight=1, minsize=10)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(6, weight=0, minsize=10)

    def bind_markerlabel_entries(self):
        for i, entry in enumerate(self.markerlabel_entries):
            # Use a closure to capture the current state properly
            entry.bind("<FocusIn>", lambda e, entry=entry: self.set_entry_focus(True))
            entry.bind("<FocusOut>", lambda e, entry=entry: self.set_entry_focus(False))
            # Allow Return key to defocus entry
            entry.bind("<Return>", lambda e, entry=entry: self.root.focus_set())

#  ██████  ██    ██ ██     ███████ ██    ██ ███    ██  ██████ ████████ ██  ██████  ███    ██ ███████ 
# ██       ██    ██ ██     ██      ██    ██ ████   ██ ██         ██    ██ ██    ██ ████   ██ ██      
# ██   ███ ██    ██ ██     █████   ██    ██ ██ ██  ██ ██         ██    ██ ██    ██ ██ ██  ██ ███████ 
# ██    ██ ██    ██ ██     ██      ██    ██ ██  ██ ██ ██         ██    ██ ██    ██ ██  ██ ██      ██ 
#  ██████   ██████  ██     ██       ██████  ██   ████  ██████    ██    ██  ██████  ██   ████ ███████ 
#                                                                                                    
#                                                                                                    
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
            # Check if the window itself has focus, not individual widgets
            self.window_focused = self.root.focus_displayof() is not None
        except (KeyError, AttributeError):
            self.window_focused = False
        self.update_hotkey_status()
        # Increase interval to reduce interference with normal GUI operations
        self.root.after(500, self.check_window_focus)
    
    def defocus_text(self, event):
        # Only defocus when clicking outside of any interactive widget
        if event.type == "2":  # KeyPress event (Return key)
            if self.window_focused and self.entry_focused:
                self.root.focus_set()
        else:  # Mouse click event
            # Only set focus to root if clicked on the root window itself
            # Don't interfere with clicks on buttons or other widgets
            if event.widget == self.root:
                self.root.focus_set()

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
        # Only handle hotkeys when hotkeys are active and not in an entry field
        if not self.hotkeys_active:
            return
            
        # Check if focus is on an entry field
        current_focus = self.root.focus_get()
        if current_focus in self.markerlabel_entries:
            return
            
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
        elif key == "p" or key == "P":
            self.add_playlist_to_file()  # Add playlist entry for 'p' or 'P'
        elif event.keysym == "Left":
            self.playlist.dec_playhead()  # Decrease playlist playhead with left arrow
        elif event.keysym == "Right":
            self.playlist.inc_playhead()  # Increase playlist playhead with right arrow
    
    def flash_button(self, index):
        self.markerlabel_entries[index].config(bootstyle="danger")
        self.root.after(500, lambda: self.markerlabel_entries[index].config(bootstyle="default"))
    
    def update_playlist_selector(self, lenght, *args):
        self.playlist_selector.configure(to=lenght)

    def auto_save_markerlabels(self):
        """Auto-saves markerlabels to the project file."""
        if self.project.project_markerlabel_file:
            try:
                markerlabel_data = "\n".join(entry.get() for entry in self.markerlabel_entries) + "\n"
                Path(self.project.project_markerlabel_file).write_text(markerlabel_data, encoding='utf-8')
                logging.debug(f"Auto-saved markerlabels to {self.project.project_markerlabel_file}")
            except Exception as e:
                logging.error(f"Failed to auto-save markerlabels: {e}")

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
        Used as callback function for loading projects.
        """
        if self.project.project_isvalid and self.project.project_name:
            self.file_label.config(text=f"Project: {self.project.project_name}")
            self.file_labelframe.config(bootstyle="success")
            self.load_project_history()
        else:
            self.file_label.config(text="No project loaded.")
            self.file_labelframe.config(bootstyle="warning")

# ███████ ██ ██      ███████ ███████     ██   ██  █████  ███    ██ ██████  ██      ██ ███    ██  ██████  
# ██      ██ ██      ██      ██          ██   ██ ██   ██ ████   ██ ██   ██ ██      ██ ████   ██ ██       
# █████   ██ ██      █████   ███████     ███████ ███████ ██ ██  ██ ██   ██ ██      ██ ██ ██  ██ ██   ███ 
# ██      ██ ██      ██           ██     ██   ██ ██   ██ ██  ██ ██ ██   ██ ██      ██ ██  ██ ██ ██    ██ 
# ██      ██ ███████ ███████ ███████     ██   ██ ██   ██ ██   ████ ██████  ███████ ██ ██   ████  ██████  
#                                                                                                        
#                                                                                                 
    def _load_recent_project(self, project_path: str):
        """
        Callback method to load a project from recent projects list.
        
        Args:
            project_path: Path to the project folder
        """
        try:
            self.project.load_project(project_path)
        except Exception as e:
            logging.error(f"Error loading recent project: {e}")
            Messagebox.show_error(
                title="Error loading project",
                message=f"Failed to load project:\n{str(e)}"
            )

    def load_project_content(self):
        """
        Loads markerlabels and playlist content from the current project files.
        """
        try:
            # Load markerlabels if file exists
            if (self.project.project_markerlabel_file and 
                Path(self.project.project_markerlabel_file).exists()):
                
                from markerlabel import load_markerlabel
                load_markerlabel(self, self.project.project_markerlabel_file)
                logging.info(f"Loaded markerlabels from project: {self.project.project_markerlabel_file}")
            
            # Load playlist if file exists
            if (self.project.project_playlist_file and 
                Path(self.project.project_playlist_file).exists()):
                
                self.playlist.load_from_project()
                
        except Exception as e:
            logging.error(f"Error loading project content: {e}")

    def get_default_directory(self):
        """
        Gets the default directory from settings if it exists and is valid.
        Returns None if not set or invalid.
        """
        default_dir = self.settings_manager.get_setting('default_dir')
        if default_dir and Path(default_dir).exists() and Path(default_dir).is_dir():
            return default_dir
        return None

    def create_new_file(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"EDL_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                initialdir=self.get_default_directory(),
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
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            initialdir=self.get_default_directory()
        )
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
        # Use current_dir if available, otherwise default directory from settings
        initial_dir = self.current_dir or self.get_default_directory()
        
        save_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            defaultextension=".txt",
            initialfile=f"Markerlabels_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if save_path:
            save_path = Path(save_path)
            save_path.write_text("\n".join(entry.get() for entry in self.markerlabel_entries) + "\n")

    def open_markerlabels(self):
        # Use current_dir if available, otherwise default directory from settings
        initial_dir = self.current_dir or self.get_default_directory()
        
        load_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            initialdir=initial_dir
        )
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
        # Load settings using the new settings manager
        settings_data = self.settings_manager.load_settings()

        # apply theme
        theme = settings_data.get('theme', 'darkly')
        try:
            # Apply theme to the existing root window
            self.root.style.theme_use(theme)
            logging.info(f"Theme set to: {theme}")
        except Exception as e:
            logging.warning(f"Failed to set theme '{theme}', falling back to 'darkly': {e}")
            try:
                self.root.style.theme_use("darkly")
            except Exception:
                logging.error("Failed to set fallback theme")
                pass

        # Apply settings to instance variables
        self.log_level = settings_data.get('log_level', self.log_level)
        self.funny = settings_data.get('funny', self.funny)
        self.default_dir = settings_data.get('default_dir', self.default_dir)
        self.delete_key = settings_data.get('delete_key', self.delete_key)
        
        # Update recent projects manager with max_recent setting
        max_recent = settings_data.get('max_recent', 5)
        if hasattr(self, 'recent_manager'):
            self.recent_manager.update_max_recent(max_recent)
            # Update recent menu if it exists
            if hasattr(self, 'recent_menu') and self.recent_menu:
                self.recent_menu.update_submenu()
        
        # Set log level
        logging.getLogger().setLevel(self.log_level)
        logging.info(f"Logging level set to {self.log_level}")
        
        # Update settings folder reference
        self.settings_folder = self.settings_manager.get_settings_folder_path()
        self.settings_folder_str = StringVar(value=str(self.settings_folder))
        
        # Try to load markerlabels from legacy file
        if self.settings_folder.exists():
            load_path = self.settings_folder / "texts.txt"
            if load_path.exists():
                self.import_markerlabels(load_path)
                logging.info(f"Imported markerlabels and settings from {load_path}")
            else:
                return
        else:
            logging.info("No markerlabels loaded.")
    
    def load_default_markerlabels(self):
        settings_folder = self.settings_manager.get_settings_folder_path()
        if settings_folder.exists():
            load_path = settings_folder / "texts.txt"
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

    def on_project_update(self):
        """
        Callback function called when a project is updated/loaded.
        Updates the display and loads project content (markerlabels and playlist).
        """
        # Update the display first
        self.update_project_display()
        
        # Load project content if project is valid
        if self.project.project_isvalid:
            self.load_project_content()
            
            # Add to recent projects if project is valid
            if self.project.project_name and self.project.project_path:
                self.recent_manager.add_project(
                    self.project.project_name, 
                    str(self.project.project_path)
                )
                # Update recent projects menu
                if self.recent_menu:
                    self.recent_menu.update_submenu()

# ███    ███  █████  ██████  ██   ██ ███████ ██████  ███████ 
# ████  ████ ██   ██ ██   ██ ██  ██  ██      ██   ██ ██      
# ██ ████ ██ ███████ ██████  █████   █████   ██████  ███████ 
# ██  ██  ██ ██   ██ ██   ██ ██  ██  ██      ██   ██      ██ 
# ██      ██ ██   ██ ██   ██ ██   ██ ███████ ██   ██ ███████ 
#                                                            
#                                                            
    def add_to_file(self, index, *args):
        # Use project EDL file if available, otherwise fall back to standalone file
        edl_file = self.project.project_edl_file if self.project.project_edl_file else self.file_path
        
        if self.hotkeys_active and edl_file:
            text = self.markerlabel_entries[index].get()
            if not text and self.funny:
                text = random_markerlabel(self)
            elif not text and not self.funny:
                text = f"Button {index +1}"
            marker = f"{datetime.now().strftime('%H:%M:%S')} - {text}"
            with Path(edl_file).open('a') as file:
                file.write(marker + "\n")
            self.update_last_markers(marker)        
        else:
            self.entry_error()

    def add_playlist_to_file(self):
        """Add current playlist entry to EDL file"""
        # Use project EDL file if available, otherwise fall back to standalone file
        edl_file = self.project.project_edl_file if self.project.project_edl_file else self.file_path
        
        if self.hotkeys_active and edl_file:
            try:
                # Get current playlist entry (this also increments the playhead)
                playlist_text = self.playlist.playlist_entry()
                if playlist_text:
                    marker = f"{datetime.now().strftime('%H:%M:%S')} - {playlist_text}"
                    with Path(edl_file).open('a') as file:
                        file.write(marker + "\n")
                    self.update_last_markers(marker)
                else:
                    logging.warning("No playlist entry available")
            except Exception as e:
                logging.error(f"Error adding playlist entry to file: {e}")
                self.entry_error()
        else:
            self.entry_error()

    def add_with_popup(self):
        edl_file = self.project.project_edl_file if self.project.project_edl_file else self.file_path
        
        if self.hotkeys_active and edl_file:
            timestamp = datetime.now().strftime("%H:%M:%S")
            marker = f"{timestamp} - "

            def get_input(event=None):
                text_input = input_var.get()
                popup.destroy()
                if text_input:
                    marker_popup = marker + text_input
                    with Path(edl_file).open('a') as file:
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
        # Only handle backspace for deletion when not in an entry field
        current_focus = self.root.focus_get()
        if current_focus not in self.markerlabel_entries and self.delete_key and self.hotkeys_active:
            self.delete_last_marker()

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
            if self.last_markers:  # Check if there are markers to remove
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


    def entry_error(self):
        if not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")
        else:
            Messagebox.show_error("No project loaded. Please create or load a project first.")

# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 
#                                 
#                                 
if __name__ == "__main__":
    try:
        #XXX Create window without fixed theme - theme will be set in load_settings()
        root = ttk.Window()
        app = QuickEDLApp(root)
        app.load_settings() #INSPECT load settings in app init?
        root.mainloop()
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise
