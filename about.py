import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser

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
    
    label1 = ttk.Label(aboutscreen, text=f"QuickEDL {version}", font=("Courier New", 14))
    label1.pack(padx=10, pady=20)

    label2 = ttk.Label(aboutscreen, text="© 2024, Eric Kirchheim")
    label2.pack()

    urlQuickedl = "https://www.github.com/punkerschaf/quickedl"
    label3 =ttk.Label(aboutscreen, text=urlQuickedl, cursor="hand2")
    label3.pack()
    label3.bind("<Button-1>", lambda e: callback(urlQuickedl))

