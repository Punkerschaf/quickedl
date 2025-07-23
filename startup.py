"""
This file is part of QuickEDL.
It creates and handles a message on application startup.
"""

import logging
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification
from version import VERSION

class StartupToast:
    """
    Class to create a startup message.
    """

    def __init__(self, **kwargs):
        self.version = VERSION
        self.message = f"QuickEDL {self.version}"
        self.toast = ToastNotification(
            title="QuickEDL",
            message=self.message,
            bootstyle="success",
            icon="",
            duration=5000
            )
    
    def addline(self, text):
        """
        Add a line to the message.
        """
        self.message += f"\n{text}"
        self.toast.message = self.message
    
    def show(self):
        """
        Show the toast notification.
        """
        self.toast.show_toast()
        logging.info(f"Startup message: {self.message}")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    startup = StartupToast()
    startup.addline("Das hier ist eine Info.")
    startup.addline("Und eine andere Information")
    startup.show()
    root.mainloop()