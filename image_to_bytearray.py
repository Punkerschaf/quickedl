from PIL import Image
import io

# Bildpfad
image_path = "resources/icon_unix.png"

# Bild öffnen und in ein Byte-Array konvertieren
with open(image_path, "rb") as image_file:
    bin_logo = image_file.read()

# Byte-Array in eine Python-Datei speichern
with open("logo.py", "w") as py_file:
    py_file.write(f"image_data = {bin_logo!r}")