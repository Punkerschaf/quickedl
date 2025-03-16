import ttkbootstrap as ttk

from tkinter import filedialog, StringVar, BooleanVar
from pathlib import Path

import logging

class Playlist():
    def __init__(self, **kwargs):
        """
        Creates an playlist instance.

        Objects:
            playhead: ttk.IntVar
                Used by Widget as index to point at list
            
            playhead_text: ttk.StrVar
                Usef by Widget as text from list
            
            data_len: ttk.IntVar
                Used by spinbox widget as dynamic list lenght.
            
            inc_able / dec_able: BooleanVar
                Are True, when playhead increasable and decreasable.
        
        Functions:
            playlist_edit_window(): Shows the playlist editor
            change_playhead(new_value): change playhead position
            playlist_entry(): returns current playlist text as String and increments playhead after that.
        """
        self.data = ["No Items"]
        self.data_len = ttk.IntVar(value=len(self.data))
        self.data_len.trace_add("write", self.update_decinc_able)

        self.playhead = ttk.IntVar(value=0)
        self.playhead.trace_add("write", self.on_playhead_update)
        self.playhead.trace_add("write", self.update_decinc_able)
        
        self.playhead_text = StringVar(value=self.data[self.playhead.get()])

        self.inc_able = BooleanVar(value=self.playhead.get() < (self.data_len.get()-1))
        self.dec_able = BooleanVar(value=self.playhead.get() > 0)

        self.edit_window = None
        self.directory = kwargs.get('directory', Path.home())
        logging.debug("Playlist initialized.")
    

    def playlist_edit_window(self):
        """
        Open window to edit the playlist of existing Playlist instance.
        """
        self.edit_window_focused = False

        if self.edit_window is not None and self.edit_window.winfo_exists():
            self.edit_window.lift()
            return

        self.edit_window = ttk.Toplevel()
        self.edit_window.title("QuickEDL: Edit Playlist")
        self.edit_window.geometry("400x500")
        self.edit_window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.edit_window.columnconfigure(1, weight=1)
        self.edit_window.columnconfigure(2, weight=1)
        self.edit_window.columnconfigure(3, weight=1)
        self.edit_window.columnconfigure(4, weight=1)
        self.edit_window.columnconfigure(5, weight=0)

        self.edit_window.rowconfigure(1, weight=1)
        self.edit_window.rowconfigure(2, weight=0)
        self.edit_window.rowconfigure(3, weight=0)

        # text field
        self.text_area = ttk.Text(self.edit_window, wrap="none", height=15)
        self.text_area.grid(column=1, columnspan=4, row=1, sticky="NSEW")
        
        self.text_area.bind("<Button-3>", self.show_text_context_menu)

        scroll_bar = ttk.Scrollbar(self.edit_window, command=self.text_area.yview)
        scroll_bar.grid(column=5, row=1, sticky="NS")
        self.text_area.configure(yscrollcommand=scroll_bar.set)

        # context menu
        self.text_ctx_menu = ttk.Menu(self.edit_window, tearoff=0)
        self.text_ctx_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.text_ctx_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.text_ctx_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))

        # Buttons
        ttk.Button(self.edit_window, text="Update", command=self.update_list).grid(column=1, row=2, padx=5, pady=5)
        ttk.Button(self.edit_window, text="Load", command=self.load_playlist, bootstyle="primary-outline").grid(column=2, row=2, padx=5, pady=5)
        ttk.Button(self.edit_window, text="Save", command=self.safe_playlist, bootstyle="primary-outline").grid(column=3, row=2, padx=5, pady=5)

        self.populate_text_area()

        self.edit_window.bind("<FocusIn>", self.on_edit_window_focus_in)
        self.edit_window.bind("<FocusOut>", self.on_edit_window_focus_out)
        self.edit_window.bind("<Button-1>", self.on_edit_window_click)


    # GUI: WINDOW
    def on_edit_window_focus_in(self, event):
        self.edit_window_focused = True

    def on_edit_window_focus_out(self, event):
        self.edit_window_focused = False

    def on_edit_window_click(self, event):
        if event.widget == self.text_area:  # Direkte Referenzprüfung statt String-Vergleich
            self.text_area.focus_set()  # Explizit Fokus auf das Text-Widget setzen
            return
        if not isinstance(event.widget, ttk.Button):
            self.edit_window.focus_set()

    def close_window(self):
        self.edit_window.destroy()
        self.edit_window = None

    def populate_text_area(self):
        self.text_area.delete("1.0", "end")
        for line in self.data:
            self.text_area.insert("end", line + "\n")

    def update_list(self):
        self.data = self.text_area.get("1.0", "end").splitlines()
        logging.debug("Playlist updated from text.")


    # ITEM CONTROL
    def add_item(self):
        new_entry = f"Eintrag {len(self.data) + 1}"
        self.data.append(new_entry)
        self.populate_text_area()
        self.update_data_len()

    def remove_item(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            del self.data[index]
            self.populate_text_area()
            self.update_data_len()

    def move_up(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index > 0:
                self.data[index], self.data[index - 1] = self.data[index - 1], self.data[index]
                self.populate_text_area()
                self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.data) - 1:
                self.data[index], self.data[index + 1] = self.data[index + 1], self.data[index]
                self.populate_text_area()
                self.tree.selection_set(self.tree.get_children()[index + 1])

    def edit_item(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            entry = ttk.Entry(self.edit_window)
            entry.insert(0, item['text'])
            entry.bind("<Return>", lambda e: self.save_item(entry, selected[0]))
            entry.bind("<Tab>", lambda e: self.save_item(entry, selected[0], focus_next=True))
            entry.grid(row=self.tree.index(selected[0]) + 1, column=1, columnspan=4, sticky="nsew")
            entry.focus()

    def save_item(self, entry, item_id, focus_next=False):
        new_value = entry.get()
        index = self.tree.index(item_id)
        self.data[index] = new_value
        self.populate_text_area()
        if focus_next:
            next_index = (index + 1) % len(self.data)
            self.tree.selection_set(self.tree.get_children()[next_index])
            self.edit_item(None)
        entry.destroy()

    def defocus_item(self, event):
        self.edit_window.focus()

    def focus_next_item(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            next_index = (index + 1) % len(self.data)
            self.tree.selection_set(self.tree.get_children()[next_index])
            self.edit_item(None)
    
    def update_data_len(self):
        self.data_len.set(len(self.data))
        logging.debug(f"updated data_len to {self.data_len.get()}")

    def update_decinc_able(self, *args):
        """
        Updates the dec_able and inc_able variables based on the current playhead position.
        """
        current = self.playhead.get()
        self.inc_able.set(current < (self.data_len.get() - 1))
        self.dec_able.set(current > 0)
        logging.debug(f"Updated inc_able to {self.inc_able.get()} and dec_able to {self.dec_able.get()}")


    # PLAYHEAD CONTROL    
    def inc_playhead(self):
        """
        Increments the playhead.
        """
        current = int(self.playhead.get())
        lenght = len(self.data)
        if 0 <= current < lenght-1:
            self.playhead.set(current +1)
            logging.debug(f"Playlist: Incrementing playhead to {self.playhead.get()}")

    def dec_playhead(self):
        """
        Decrements the playhead.
        """
        current = int(self.playhead.get())
        lenght = len(self.data)
        if 0 < current <= lenght-1:
            self.playhead.set(current -1)
            logging.debug(f"Playlist: Decrementing playhead to {self.playhead.get()}")

    def on_playhead_update(self, *args):
        index = self.playhead.get()
        if 0 <= index < len(self.data):
            self.playhead_text.set(self.data[index])
    
    def playlist_entry(self, *args):
        """
        Returns current playlist entry as string and increments playhead after that.
        
        Return:
            playlist_entry: str
        """
        index = self.playhead.get()
        lenght = len(self.data)
        if 0 <= index <= lenght-1:
            string = str(self.data[index])
            if not index == lenght-1:
                self.playhead.set(self.playhead.get()+1)
            return string
        else:
            logging.error(f"Playlist.playlist_entry: Index out of range ({index} from {self.playhead.get()})")


    # FILE HANDLING
    def safe_playlist(self):
        save_path = filedialog.asksaveasfilename(
            initialdir=self.directory,
            defaultextension=".txt",
            initialfile="Playlist.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if save_path:
            save_path = Path(save_path)
            save_path.write_text("\n".join(self.data))
    
    def load_playlist(self):
        load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")],
                                               initialdir=self.directory)
        if load_path:
            load_path = Path(load_path)
            self.data = load_path.read_text().splitlines()
            self.update_data_len()
            self.populate_text_area()

    def show_text_context_menu(self, event):
        """Zeigt das Kontextmenü für das Textfeld an"""
        try:
            # Die Methode tk_popup ist zuverlässiger für Kontextmenüs als post
            # Der dritte Parameter '0' gibt an, dass das Menü sofort erscheinen soll
            self.text_ctx_menu.tk_popup(event.x_root, event.y_root, 0)
            # Wichtig: Das Event hier stoppen, damit es nicht weitergeleitet wird
            return "break"
        except Exception as e:
            logging.error(f"Fehler beim Anzeigen des Kontextmenüs: {e}")
        finally:
            # Immer den Grab freigeben
            self.text_ctx_menu.grab_release()


# EXEC
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    playlist = Playlist()
    playlist.playlist_edit_window()
    root.mainloop()