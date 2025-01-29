import random
import ttkbootstrap as ttk
from tkinter import Canvas, Toplevel

class ConfettiApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Konfetti-Animation")
        self.geometry("600x400")

        # Beispielinhalt im Fenster
        ttk.Label(self, text="Konfetti-Animation über das gesamte Fenster", font=("Arial", 16)).pack(pady=20)
        ttk.Button(self, text="Start Konfetti", command=self.show_confetti).pack(pady=20)

    def show_confetti(self):
        # Erstelle ein Overlay-Fenster für die Animation
        overlay = Toplevel(self)
        overlay.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_rootx()}+{self.winfo_rooty()}")
        overlay.overrideredirect(True)  # Entfernt Fensterrahmen
        overlay.attributes("-topmost", True)  # Bringt Overlay nach vorne
        overlay.attributes("-alpha", "1.0")  # Macht Hintergrund weiß transparent

        # Canvas für Konfetti
        canvas = Canvas(overlay, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        confetti = []  # Liste der Konfettistücke

        # Konfetti-Objekte erzeugen
        for _ in range(50):
            x = random.randint(0, self.winfo_width())
            y = random.randint(-50, 0)  # Start über dem sichtbaren Bereich
            size = random.randint(5, 15)
            color = random.choice(["red", "blue", "green", "yellow", "pink", "purple"])
            oval = canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
            confetti.append((oval, random.uniform(2, 5)))  # Geschwindigkeit speichern

        def animate():
            for item, speed in confetti:
                canvas.move(item, 0, speed)  # Bewege das Konfetti nach unten
                x, y, _, _ = canvas.coords(item)

                # Wenn das Konfetti unten aus dem Fenster verschwindet, setze es oben neu
                if y > self.winfo_height():
                    new_x = random.randint(0, self.winfo_width())
                    canvas.coords(item, new_x, -10, new_x + size, -10 + size)

            # Animation fortsetzen
            canvas.after(20, animate)

        def close_overlay():
            overlay.destroy()

        # Starte Animation
        animate()

        # Beende Overlay nach 3 Sekunden
        self.after(3000, close_overlay)


if __name__ == "__main__":
    app = ConfettiApp()
    app.mainloop()
