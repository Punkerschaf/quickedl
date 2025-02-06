import ttkbootstrap as ttk

from tkinter import filedialog, StringVar
from pathlib import Path

import logging

class Playlist():
    def __init__(self, **kwargs):
        self.data = ["No Items"]
        self.playhead = 0
        self.playhead_stringvar = StringVar(value=str(self.data[self.playhead]))
        self.edit_window = None
        self.directory = kwargs.get('directory', Path.home())
        logging.debug("Playlist initialized.")
    
    def playlist_edit_window(self):
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

        # Treeview
        self.tree_scroll = ttk.Scrollbar(self.edit_window)
        self.tree_scroll.grid(column=5, row=1, sticky="N, S")

        self.tree = ttk.Treeview(self.edit_window, show="tree", yscrollcommand=self.tree_scroll.set, height=15)
        self.tree.grid(column=1, columnspan=4, row=1, sticky="NSEW")
        self.tree_scroll.config(command=self.tree.yview)

        self.tree.bind("<Double-1>", self.edit_item)
        self.tree.bind("<Return>", self.defocus_item)
        self.tree.bind("<Tab>", self.focus_next_item)

        # Buttons
        ttk.Button(self.edit_window, text="New", command=self.add_item, bootstyle="success").grid(column=1, row=2, padx=5, pady=5)
        ttk.Button(self.edit_window, text="Del", command=self.remove_item, bootstyle="danger").grid(column=2, row=2, padx=5, pady=5)
        ttk.Button(self.edit_window, text="Move Up", command=self.move_up, bootstyle="primary").grid(column=3, row=2, padx=5, pady=5)
        ttk.Button(self.edit_window, text="Move Down", command=self.move_down, bootstyle="primary").grid(column=4, row=2, padx=5, pady=5)

        ttk.Button(self.edit_window, text="Load", command=self.load_playlist, bootstyle="primary-outline").grid(column=1, row=3, padx=5, pady=5)
        ttk.Button(self.edit_window, text="Save", command=self.safe_playlist, bootstyle="primary-outline").grid(column=2, row=3, padx=5, pady=5)

        self.populate_list()

    def close_window(self):
        self.edit_window.destroy()
        self.edit_window = None

    def populate_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.data:
            self.tree.insert("", "end", values=(entry,), text=entry)

    def add_item(self):
        new_entry = f"Eintrag {len(self.data) + 1}"
        self.data.append(new_entry)
        self.populate_list()

    def remove_item(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            del self.data[index]
            self.populate_list()

    def move_up(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index > 0:
                self.data[index], self.data[index - 1] = self.data[index - 1], self.data[index]
                self.populate_list()
                self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.data) - 1:
                self.data[index], self.data[index + 1] = self.data[index + 1], self.data[index]
                self.populate_list()
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
        self.populate_list()
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
    
    def get_current_item(self):
        """Returns the current list item."""
        if 0 <= self.playhead < len(self.data):
            return self.data[self.playhead]
        return None

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
            self.populate_list()


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    playlist = Playlist()
    playlist.playlist_edit_window()
    root.mainloop()