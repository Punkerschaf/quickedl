import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from tkinter import filedialog

class QuickEDLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickEDL v1.3.1")
        self.root.geometry("600x700")

        # Set dark theme
        self.style = ttk.Style("darkly")

        # File path for current EDL
        self.file_path = None
        self.last_entries = []

        # Hotkey status
        self.hotkeys_active = True

        # Create menu
        self.create_menu()

        # Create widgets
        self.create_widgets()

        self.check_window_focus()


    def create_menu(self):
        menu_bar = ttk.Menu(self.root)

        edl_menu = ttk.Menu(menu_bar, tearoff=0)
        edl_menu.add_command(label="New EDL", command=self.create_new_file)
        edl_menu.add_command(label="Open EDL", command=self.load_file)
        edl_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="EDL", menu=edl_menu)

        texts_menu = ttk.Menu(menu_bar, tearoff=0)
        texts_menu.add_command(label="Save Texts", command=self.save_texts)
        texts_menu.add_command(label="Load Texts", command=self.load_texts)
        menu_bar.add_cascade(label="Texts", menu=texts_menu)

        export_menu = ttk.Menu(menu_bar, tearoff=0)
        export_menu.add_command(label="Export CMX", command=self.export_cmx)
        export_menu.add_command(label="Export FCP7 XML", command=self.export_fcp7)
        menu_bar.add_cascade(label="Export", menu=export_menu)

        self.root.config(menu=menu_bar)

    def create_widgets(self):
        # Bind click to root for defocusing text fields
        self.root.bind("<Button-1>", self.defocus_text)
        # Time display
        self.time_label = ttk.Label(self.root, text="", font=("Courier New", 30))
        self.time_label.pack(pady=10)
        self.update_time()

        # File label
        self.file_label = ttk.Label(self.root, text="No EDL file loaded.")
        self.file_label.pack(pady=10)

        # Hotkey status label
        self.hotkey_status = ttk.Label(self.root, text="Hotkeys Active", font=("Helvetica", 10), foreground="green")
        self.hotkey_status.pack(pady=5)

        # Text entry fields
        self.text_entries = []
        for i in range(9):
            frame = ttk.Frame(self.root)
            frame.pack(pady=5)

            entry = ttk.Entry(frame, width=40)
            entry.pack(side=LEFT, padx=10)
            self.text_entries.append(entry)

            # Bind focus events to update hotkey status
            entry.bind("<FocusIn>", lambda e: self.set_hotkeys_active(False))
            entry.bind("<FocusOut>", lambda e: self.set_hotkeys_active(True))

            button = ttk.Button(frame, text=f"Button {i + 1}", command=lambda i=i: self.add_to_file(i))
            button.pack(side=RIGHT)

        # Popup button
        popup_button = ttk.Button(self.root, text="Button 10 (Add with Popup)", command=self.add_with_popup)
        popup_button.pack(pady=10)

        # Separator button
        separator_button = ttk.Button(self.root, text="Button 11 (Separator)", command=self.add_separator)
        separator_button.pack(pady=10)

        # Last entries display
        self.last_entries_text = ttk.StringVar(value="No entries yet.")
        last_entries_label = ttk.Label(self.root, textvariable=self.last_entries_text, justify=LEFT)
        last_entries_label.pack(pady=10)

    def defocus_text(self, event):
        # Check if click is outside text fields
        if event.widget not in self.text_entries:
            self.root.focus_set()  # Remove focus from any widget
            self.set_hotkeys_active(True)
    
    def check_window_focus(self):
        # Prüfen, ob das Fenster innerhalb des Betriebssystems den Fokus hat
        if self.root.focus_displayof():
            self.hotkeys_active = True
            self.hotkey_status.config(text="Hotkeys Active", foreground="green")
        else:
            self.hotkeys_active = False
            self.hotkey_status.config(text="Hotkeys Inactive", foreground="red")
        # Alle 100 ms den Fokusstatus erneut prüfen
        self.root.after(100, self.check_window_focus)

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def set_hotkeys_active(self, active):
        self.hotkeys_active = active
        status_text = "Hotkeys Active" if active else "Hotkeys Inactive"
        status_color = "green" if active else "red"
        self.hotkey_status.config(text=status_text, foreground=status_color)

    def create_new_file(self):
        self.file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"EDL_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if self.file_path:
            with open(self.file_path, 'w') as file:
                file.write("File created on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            self.file_label.config(text=f"EDL file created: {self.file_path}")

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            self.file_label.config(text=f"EDL file loaded: {self.file_path}")

    def save_texts(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"TextFields_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if save_path:
            with open(save_path, 'w') as file:
                for entry in self.text_entries:
                    file.write(entry.get() + "\n")

    def load_texts(self):
        load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if load_path:
            with open(load_path, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines[:9]):
                    self.text_entries[i].delete(0, END)
                    self.text_entries[i].insert(0, line.strip())

    def add_to_file(self, index):
        if self.hotkeys_active and self.file_path:
            text = self.text_entries[index].get()
            entry = f"{datetime.now().strftime('%H:%M:%S')} - {text}"
            with open(self.file_path, 'a') as file:
                file.write(entry + "\n")
            self.update_last_entries(entry)
        elif not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")
        else:
            Messagebox.show_error("No EDL file has been created. Please create a file first.")

    def add_with_popup(self):
        if self.hotkeys_active and self.file_path:
            timestamp = datetime.now().strftime("%H:%M:%S")
            entry = f"{timestamp} - "
            text_input = Messagebox.prompt("Input", "Enter your text:")
            if text_input:
                entry += text_input
                with open(self.file_path, 'a') as file:
                    file.write(entry + "\n")
                self.update_last_entries(entry)
        elif not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")
        else:
            Messagebox.show_error("No EDL file has been created. Please create a file first.")

    def add_separator(self):
        if self.hotkeys_active and self.file_path:
            separator = "-" * 40
            with open(self.file_path, 'a') as file:
                file.write(separator + "\n")
            self.update_last_entries(separator)
        elif not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")
        else:
            Messagebox.show_error("No EDL file has been created. Please create a file first.")

    def update_last_entries(self, new_entry):
        self.last_entries.append(new_entry)
        if len(self.last_entries) > 5:
            self.last_entries.pop(0)
        self.last_entries_text.set("\n".join(self.last_entries))

    def export_cmx(self):
        # Placeholder for CMX export
        Messagebox.show_info("Export CMX", "Export CMX functionality is not implemented yet.")

    def export_fcp7(self):
        # Placeholder for FCP7 export
        Messagebox.show_info("Export FCP7", "Export FCP7 XML functionality is not implemented yet.")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = QuickEDLApp(root)
    root.mainloop()
