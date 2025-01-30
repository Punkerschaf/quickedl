import random
from tkinter import Canvas, Toplevel

def show_confetti(window):
    """
    Shows a confetti animation on a toplevel window.

    Args:
        window: window on which the animation is show.
    
    Return:
        toplevel window on window
    """
    # Erstelle ein Overlay-Fenster für die Animation
    overlay = Toplevel(window)
    overlay.geometry(f"{window.winfo_width()}x{window.winfo_height()}+{window.winfo_rootx()}+{window.winfo_rooty()}")
    overlay.overrideredirect(True)  # Entfernt Fensterrahmen
    overlay.attributes("-topmost", True)  # Bringt Overlay nach vorne
    overlay.attributes("-alpha", 0.0)  # Macht Hintergrund transparent
    overlay.lift()  # Bringt das Overlay-Fenster in den Vordergrund

    # Canvas für Konfetti
    canvas = Canvas(overlay, bg="white", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    confetti = []  # Liste der Konfettistücke

    # Konfetti-Objekte erzeugen
    for _ in range(50):
        x = random.randint(0, window.winfo_width())
        y = random.randint(-50, 0)  # Start über dem sichtbaren Bereich
        size = random.randint(5, 15)
        color = random.choice(["lightcoral", "lightblue", "lightgreen", "lightyellow", "lightpink", "lavender", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightsalmon"])
        oval = canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
        confetti.append((oval, random.uniform(2, 5)))  # Geschwindigkeit speichern

    def animate():
        for item, speed in confetti:
            canvas.move(item, 0, speed)  # Bewege das Konfetti nach unten
            x, y, _, _ = canvas.coords(item)

            # Wenn das Konfetti unten aus dem Fenster verschwindet, setze es oben neu
            if y > window.winfo_height():
                new_x = random.randint(0, window.winfo_width())
                canvas.coords(item, new_x, -10, new_x + size, -10 + size)
        canvas.after(20, animate)

    def close_overlay():
        overlay.destroy()
    
    animate()

    window.after(3000, close_overlay)