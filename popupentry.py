import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

### NICHT TTKBS-FAEHIG

def add_with_popup(self):
        if self.hotkeys_active and self.file_path:
            text_input = Messagebox.prompt("Input", "Enter your text:")
            if text_input:
                entry += text_input
                with open(self.file_path, 'a') as file:
                    file.write(entry + "\n")
                self.update_last_entries(entry)
        elif not self.hotkeys_active:
            Messagebox.show_error("Hotkeys are inactive. Please click outside text fields to enable.")