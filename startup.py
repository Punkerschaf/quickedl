"""
This file is part of QuickEDL.
It creates and handles a toast message on application startup.
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
        self.style = "success"
        self.toast = None
    
    def addline(self, text, warning=False):
        """
        Add a line to the message.
        Args:
            text -> String: Text to add to the message
            warning -> Bool: If True, set style to warning
        """
        self.message += f"\n{text}"
        if warning:
            self.style = "warning"
    
    def show(self):
        """
        Show the toast notification.
        """
        self.toast = ToastNotification(
            title="QuickEDL",
            message=self.message,
            bootstyle=self.style,
            icon="",
            duration=5000
            )
        self.toast.show_toast()
        logging.info(f"Startup message: {self.message}")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    startup = StartupToast()
    startup.addline("Das hier ist eine Info.")
    startup.addline("Und eine andere Information", True)
    startup.show()
    root.mainloop()