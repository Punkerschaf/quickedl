import random

funny_entries = [
"Kaffee ist alle",
"Mein Rechter, Rechter Platz ist frei",
"Bezahlte Werbung",
"Unterstützt durch Produktplatzierung",
"Heute ist ein guter Tag für ein Nickerchen.",
"404: Eintrag nicht gefunden.",
"Zufallseintrag erstellt"
]

def random_entry(self):
    random_entry = random.choice(funny_entries)
    return random_entry