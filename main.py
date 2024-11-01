# QuickEDL
# 2024 / Eric Kirchheim (punkerschaf)

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime
# import os

from export_cmx import export_cmx

# version number
version = "1.3"

""" MERGE LIST
- fokus indicator
"""

# Function to update the time displayed in the label
def update_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    time_label.config(text=current_time)
    window.after(1000, update_time)  # Update every second

# Function to create a new text file
def create_new_file():
    global file_path
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile=f"EDL_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
        filetypes=[("Text files", "*.txt")]
    )
    if file_path:
        with open(file_path, 'w') as file:
            file.write("File created on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        file_label.config(text=f"EDL file created: {file_path}")

def load_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path) as file:
            file_label.config(text=f"EDL file loaded: {file_path}")

# Function to show error message if no file is created
def show_error():
    messagebox.showerror("Error", "No EDL file has been created. Please create a file first.")

# Function to append a new line to the file and update the display of the last 5 entries
def add_to_file(index):
    if file_path:
        text = text_entries[index].get()
        entry = f"{datetime.now().strftime('%H:%M:%S')} - {text}"
        with open(file_path, 'a') as file:
            file.write(entry + "\n")
        update_last_entries(entry)
    else:
        show_error()

# Function to add a separator line and update the last 5 entries display
def add_separator():
    if file_path:
        separator = "-" * 40
        with open(file_path, 'a') as file:
            file.write(separator + "\n")
        update_last_entries(separator)
    else:
        show_error()

# Function to save the content of the text fields to a file
def save_texts():
    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile=f"TextFields_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
        filetypes=[("Text files", "*.txt")]
    )
    if save_path:
        with open(save_path, 'w') as file:
            for entry in text_entries:
                file.write(entry.get() + "\n")

# Function to load content into the text fields from a file
def load_texts():
    load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if load_path:
        with open(load_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines[:9]):  # Max 9 text fields
                text_entries[i].delete(0, tk.END)
                text_entries[i].insert(0, line.strip())

# Function to update the display of the last 5 entries
def update_last_entries(new_entry):
    last_entries.append(new_entry)
    if len(last_entries) > 5:
        last_entries.pop(0)
    last_entries_text.set("\n".join(last_entries))

# Function to handle key press events
def on_key_press(event):
    # Check if any text field has focus
    if window.focus_get() not in text_entries:
        key = event.char
        if key.isdigit():
            key_num = int(key)
            if key_num == 0:
                add_separator()  # Separator for key '0'
            elif 1 <= key_num <= 9:
                add_to_file(key_num - 1)  # Corresponding button for keys 1-9
        elif event.keysym == "space":
            add_with_popup()  # Trigger the pop-up entry for spacebar

# Function to remove focus only when clicking outside of text fields
def remove_focus(event):
    widget = event.widget
    if widget not in text_entries:
        window.focus()

# Function to handle the pop-up entry after adding an entry with a timestamp
def add_with_popup():
    if file_path:
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"{timestamp} - "
        text_input = simpledialog.askstring("Input", "Enter your text:")
        if text_input:
            entry += text_input
            with open(file_path, 'a') as file:
                file.write(entry + "\n")
            update_last_entries(entry)
    else:
        show_error()

# Function to remove focus only when clicking outside of text fields and update hotkey indicator
def remove_focus(event):
    widget = event.widget
    if widget not in text_entries:
        window.focus()
        update_hotkey_indicator()  # Refresh indicator when focus shifts to window

# Function to update the hotkey indicator based on current focus
def update_hotkey_indicator():
    focused_widget = window.focus_get()
    if focused_widget not in text_entries and window.focus_displayof() is not None:
        hotkey_status.config(text="hotkeys active", bg="red", fg="black")
    else:
        hotkey_status.config(text="hotkeys blocked", bg=default_bg_color, fg="black")


# Create the window
window = tk.Tk()
window.title(f"QuickEDL v{version}")
window.geometry("400x900")
default_bg_color = window.cget("bg")

# Bind click events to remove focus when clicking outside of text fields
window.bind("<Button-1>", remove_focus)

# Buttons to save and load the text field content
frame_saveloadtext = tk.Frame(window)
frame_saveloadtext.pack(pady=5)

save_button = tk.Button(frame_saveloadtext, text="Save Texts", command=save_texts)
save_button.pack(side="left", padx=10)

load_button = tk.Button(frame_saveloadtext, text="Load Texts", command=load_texts)
load_button.pack(side="right", padx=10)

# Button to load or create a new file
file_path = None

frame_loadcreatefile = tk.Frame(window)
frame_loadcreatefile.pack(pady=5)

create_button = tk.Button(frame_loadcreatefile, text="Load File", command=load_file)
create_button.pack(side="left", padx=10)
create_button = tk.Button(frame_loadcreatefile, text="Create New File", command=create_new_file)
create_button.pack(side="right", padx=10)

# Label to display the file path and name
file_label = tk.Label(window, text="")
file_label.pack(pady=5)

# Button for exporting to CMX 3600 format
export_button = tk.Button(window, text="Export CMX", command=lambda: export_cmx(file_path))
export_button.pack(pady=5)

# Display the current time
time_label = tk.Label(window, text="", font=("Courier New", 30))
time_label.pack(pady=5)
update_time()  # Start the time display

# label for hotkey status
hotkey_status = tk.Label(window, text="hotkeys blocked", font=("Courier New", 24), fg="black")
hotkey_status.pack(pady=5)

# Create 9 buttons and corresponding text fields
text_entries = []
buttons = []
for i in range(9):
    frame = tk.Frame(window)
    frame.pack(pady=5)
    
    entry = tk.Entry(frame, width=25)
    entry.pack(side="left", padx=10)
    text_entries.append(entry)
    
    button = tk.Button(frame, text=f"Button {i+1}", command=lambda i=i: add_to_file(i))
    button.pack(side="right")
    buttons.append(button)

# Additional button to add a timestamped entry with a pop-up input
popup_button = tk.Button(window, text="Button 10 (Add with Popup)", command=add_with_popup)
popup_button.pack(pady=10)

# Button for adding a separator line
button_11 = tk.Button(window, text="Button 11 (Separator)", command=add_separator)
button_11.pack(pady=10)

# Area to display the last 5 entries
last_entries_text = tk.StringVar()
last_entries_text.set("No entries yet.")
last_entries_label = tk.Label(window, textvariable=last_entries_text, justify="left")
last_entries_label.pack(pady=10)

# List to store the last 5 entries
last_entries = []

# Bind key press events to the corresponding functions
window.bind("<Key>", on_key_press)
window.bind("<Button-1>", remove_focus)
# Update the function that binds the focus-in and focus-out events
for entry in text_entries:
    entry.bind("<FocusIn>", lambda e: update_hotkey_indicator())
    entry.bind("<FocusOut>", lambda e: update_hotkey_indicator())

# Add a footer with version, copyright, and documentation link
footer_text = f"QuickEDL v{version} | © 2024 Eric Kirchheim | https://github.com/punkerschaf"
footer_label = tk.Label(window, text=footer_text, font=("Helvetica", 12), fg="gray")
footer_label.pack(side="bottom", pady=5)

# Start the main loop
window.mainloop()
