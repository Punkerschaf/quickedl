"""
This file is part of QuickEDL.
It provides the About dialog for the application.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa: F403
from PIL import Image, ImageTk
import io

# internal imports
from logo import bin_logo
from constants import GITHUBURL
from utils import open_in_browser

def show_about(app, version):
    aboutscreen = ttk.Toplevel()
    aboutscreen.title("About QuickEDL")
    aboutscreen.geometry("400x350")
    aboutscreen.resizable(False, False)

    def leave_about(self, event = None):
        aboutscreen.destroy()

    aboutscreen.bind("<Button-1>", leave_about)
    aboutscreen.bind("<Escape>", leave_about)

    image_stream = io.BytesIO(bin_logo)
    logo = Image.open(image_stream)
    logo = logo.resize((150, 150))
    photo = ImageTk.PhotoImage(logo)
    logo_label = ttk.Label(aboutscreen, image=photo)
    logo_label.image = photo  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=20)

    label1 = ttk.Label(aboutscreen, text=f"QuickEDL {version}", font=("Courier New", 14))
    label1.pack(padx=10, pady=10)

    label2 = ttk.Label(aboutscreen, text="© 2024-2025, Eric Kirchheim")
    label2.pack()

    githuburl = GITHUBURL
    label3 = ttk.Label(aboutscreen, text=f"{githuburl} ↗", bootstyle="info")
    label3.configure(underline=True)
    label3.pack(padx=10, pady=10)
    label3.bind("<Button-1>", lambda e: open_in_browser(githuburl))

    sep4 = ttk.Separator(aboutscreen)
    sep4.pack(fill="x", padx=10, pady=10)

    libraries = "GUI: ttkbootstrap"
    label4 = ttk.Label(aboutscreen, text=libraries)
    label4.pack()