import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
from PIL import Image, ImageTk

def callback(url):
    webbrowser.open_new(url)

def show_about(app_instance, version):
    aboutscreen = ttk.Toplevel()
    aboutscreen.title("About QuickEDL")
    aboutscreen.geometry("400x400")
    aboutscreen.resizable(False, False)

    def leave_about(self, event = None):
        aboutscreen.destroy()

    aboutscreen.bind("<Button-1>", leave_about)
    aboutscreen.bind("<Escape>", leave_about)
    
    image_path = "resources/quickedl_icon_1.png"
    logo = Image.open(image_path)
    logo = logo.resize((150, 150))
    photo = ImageTk.PhotoImage(logo)

    logo_label = ttk.Label(aboutscreen, image=photo)
    logo_label.image = photo  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=20)

    label1 = ttk.Label(aboutscreen, text=f"QuickEDL {version}", font=("Courier New", 14))
    label1.pack(padx=10)

    label2 = ttk.Label(aboutscreen, text="© 2024, Eric Kirchheim")
    label2.pack()

    urlQuickedl = "https://www.github.com/punkerschaf/quickedl"
    label3 = ttk.Label(aboutscreen, text=urlQuickedl, cursor="hand2")
    label3.pack()
    label3.bind("<Button-1>", lambda e: callback(urlQuickedl))

    sep4 = ttk.Separator(aboutscreen)
    sep4.pack(fill="x", padx=10, pady=10)

    libraries = "GUI: ttkbootstrap"
    label4 = ttk.Label(aboutscreen, text=libraries)
    label4.pack()