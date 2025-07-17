# QuickEDL Settings System

Das neue Settings-System bietet eine moderne, erweiterte Verwaltung von Anwendungseinstellungen.

## Struktur

```
settings/
├── __init__.py              # Package-Initialisierung und Kompatibilitätsfunktionen
├── settings_manager.py      # Kern-Logik für Settings-Verwaltung
├── settings_window.py       # UI für Settings-Fenster
├── example_settings.yaml    # Beispiel-Konfigurationsdatei
└── README.md               # Diese Dokumentation
```

## Features

### ✅ Universelle Settings-Verwaltung
- **YAML-basierte Konfiguration** für menschenlesbare Settings
- **Rückwärtskompatibilität** - fehlende Einstellungen werden durch Defaults ersetzt
- **Automatische Erstellung** von Settings-Ordner und -Datei bei Bedarf
- **Typ-sichere** Getter/Setter-Funktionen
- **Batch-Updates** für mehrere Einstellungen gleichzeitig

### ✅ Flexibles Interface
- **Dot-Notation** für verschachtelte Settings (`ui.theme`, `backup.enabled`)
- **Einzelne Setting-Updates** mit `set_setting(key, value)`
- **Mehrfach-Updates** mit `update_settings(dict)`
- **Reset zu Defaults** mit einem Funktionsaufruf

### ✅ Erweiterte Funktionalität
- **Recent Projects Management** für Projekte
- **Auto-Save** Einstellungen
- **Theme-Management** (Dark/Light)
- **Logging-Level** Konfiguration

### ✅ Benutzerfreundliches UI
- **Modernes Settings-Fenster** mit kategorisierten Abschnitten
- **Sofortige Anwendung** von Änderungen (z.B. Log-Level)
- **Ordner-Management** direkt aus der UI
- **Validierung** und Fehlerbehandlung

## Verwendung

### Basic Usage

```python
from settings import SettingsManager

# Initialisierung
settings = SettingsManager()

# Settings laden
config = settings.load_settings()

# Einzelne Einstellung abrufen
theme = settings.get_setting('theme', 'darkly')

# Einstellung setzen
settings.set_setting('funny', True)

# Mehrere Einstellungen aktualisieren
settings.update_settings({
    'theme': 'flatly',
    'log_level': 'INFO',
    'delete_key': True
})
```

### Settings-Fenster anzeigen

```python
from settings import show_settings_window

# Settings-Fenster öffnen
show_settings_window(app_instance)
```

### Recent Files verwalten

```python
# Recent Project hinzufügen
settings.add_recent_file('/path/to/project', 'project')

# Recent Projects abrufen
recent_projects = settings.get_setting('recent_projects', [])
```

## Rückwärtskompatibilität

Das System ist vollständig rückwärtskompatibel mit dem alten Settings-System:

```python
# Alte Funktion funktioniert weiterhin
from settings import load_yaml, show_settings_window

load_yaml(app)  # Lädt Settings in App-Objekt
show_settings_window(app)  # Zeigt Settings-Fenster
```

## Default Settings

Alle verfügbaren Einstellungen mit ihren Standardwerten:

```yaml
log_level: 'DEBUG'           # Logging-Level
funny: false                 # Zufälliger Text in leeren Feldern
default_dir: null            # Standard-Verzeichnis
delete_key: false            # Backspace löscht letzten Marker
window_geometry: '400x700'   # Fenstergröße
theme: 'darkly'              # UI-Theme (darkly/litera)
auto_save_interval: 300      # Auto-Save Intervall (Sekunden)
recent_projects: []          # Zuletzt verwendete Projekte
max_recent_files: 10         # Max. Anzahl recent files
```

## Migration

Die Migration vom alten zum neuen System erfolgt automatisch:

1. **Erste Ausführung**: Settings werden aus der bestehenden `settings.yaml` geladen
2. **Fehlende Settings**: Werden automatisch mit Defaults ergänzt
3. **Legacy Support**: Alte `texts.txt` wird weiterhin unterstützt
4. **Ordner-Struktur**: Bleibt unverändert (`~/quickedl/`)

## Entwicklung

### Neue Einstellungen hinzufügen

1. **Default-Wert** in `settings_manager.py` unter `_get_default_settings()` hinzufügen
2. **UI-Element** in `settings_window.py` erstellen
3. **Dokumentation** in `example_settings.yaml` ergänzen

### Settings-Fenster erweitern

Neue Abschnitte können in `settings_window.py` durch Hinzufügen einer `_create_*_section()` Methode erstellt werden.

## Vorteile

- ✅ **Saubere Trennung** von Logik und UI
- ✅ **Einfache Erweiterbarkeit** für neue Settings
- ✅ **Robuste Fehlerbehandlung** 
- ✅ **Vollständige Rückwärtskompatibilität**
- ✅ **Moderne YAML-Konfiguration**
- ✅ **Benutzerfreundliche UI**
