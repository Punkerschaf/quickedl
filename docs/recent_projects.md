# Recent Projects Feature - Dokumentation

## Überblick
Das Recent Projects Feature für QuickEDL ermöglicht es Benutzern, schnell auf zuletzt geöffnete Projekte zuzugreifen über ein Untermenü im Project-Menü.

## Funktionen

### Automatisches Hinzufügen
- Wenn ein neues Projekt erstellt oder ein bestehendes Projekt geladen wird, wird es automatisch zur Recent Projects Liste hinzugefügt
- Das zuletzt geladene Projekt wird an die Spitze der Liste gesetzt

### Menü-Integration
- Im Project-Menü wird ein "Recent Projects" Untermenü angezeigt
- Das Untermenü wird nur angezeigt, wenn ein Settings-Ordner existiert
- Wenn keine recent projects vorhanden sind, wird "No recent projects" angezeigt (deaktiviert)

### Intelligente Verwaltung
- Projekte werden automatisch an die Spitze der Liste verschoben, wenn sie erneut geladen werden
- Die maximale Anzahl der recent projects wird durch die Einstellung `max_recent` kontrolliert (Standard: 5)
- Ältere Einträge werden automatisch entfernt, wenn die Liste zu lang wird

### Fehlerbehandlung
- Beim Laden eines recent projects wird überprüft, ob die Datei noch existiert
- Falls das Projekt nicht mehr existiert, wird eine Fehlermeldung angezeigt und das Projekt aus der Liste entfernt
- Das Menü wird automatisch aktualisiert

## Technische Details

### Dateien
- `settings/recent.py` - Hauptimplementierung
- `settings/recent_projects.json` - Speicherort der recent projects Liste (im Settings-Ordner)

### Klassen
- `RecentProjectsManager` - Verwaltet das Laden/Speichern der recent projects
- `RecentProjectsMenu` - Verwaltet die GUI-Integration im Menü

### Einstellungen
- `max_recent`: Maximale Anzahl der recent projects (Standard: 5)
- Die Einstellung kann in `settings.yaml` oder über das Settings-Fenster geändert werden

### JSON-Format
```json
[
  {
    "name": "Projekt Name",
    "path": "/absoluter/pfad/zum/projekt/ordner"
  },
  ...
]
```

## Nutzung

### Als Benutzer
1. Erstelle oder lade ein Projekt - es wird automatisch zur Liste hinzugefügt
2. Gehe zu Project → Recent Projects im Menü
3. Klicke auf ein Projekt in der Liste um es zu laden

### Als Entwickler
Das Feature ist vollständig in die bestehende Projekt-Architektur integriert:
- Verwendet den bestehenden `update_callback` Mechanismus
- Respektiert die Settings-Manager Struktur
- Funktioniert auch ohne Settings-Ordner (Feature wird dann deaktiviert)

## Mögliche Erweiterungen
- Tastenkürzel für recent projects
- Projekt-Vorschau beim Hover
- Projektpfad in Tooltip anzeigen
- Projekte aus der Liste entfernen (rechte Maustaste)
