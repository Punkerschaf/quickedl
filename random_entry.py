import random

funny_markerlabels = [
    "Kaffee ist alle",
    "Mein Rechter, Rechter Platz ist frei",
    "Bezahlte Werbung",
    "Unterstützt durch Produktplatzierung",
    "Heute ist ein guter Tag für ein Nickerchen.",
    "404: Eintrag nicht gefunden.",
    "Zufallseintrag erstellt"
]

def random_markerlabel(self):
    """
    Select a random markerlabel from the list of funny markerlabels.

    Args:
        self: The instance of the class calling this function.

    Returns:
        str: A randomly selected markerlabel from the funny_markerlabels list.
    """
    random_markerlabel = random.choice(funny_markerlabels)
    return random_markerlabel