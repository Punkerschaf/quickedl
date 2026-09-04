# QuickEDL v4.0.0 – Roadmap

Diese Datei sammelt den aktuellen Planungsstand für den Umbau von QuickEDL als Aufgabenliste. Sie ist zum Anpassen gedacht – Reihenfolge, Scope und offene Fragen sollten vor Beginn der eigentlichen Umsetzung geprüft und ggf. korrigiert werden.

## Ziel

- Direkte Marker-Erstellung in Adobe Premiere Pro über die neue **UXP-API** (statt manuellem JSX-Export + VS-Code-ExtendScript-Debugger)
- Optionale Anbindung an **Blackmagic DaVinci Resolve**
- Komplett überarbeitete, moderne **GUI**
- Plattformunabhängig, **Open Source** (GPLv3) bleibt bestehen

## Architektur-Entscheidungen (bereits getroffen)

| Entscheidung | Ergebnis |
|---|---|
| Tech-Stack | **Python-Kern bleibt**, GUI wird auf **PySide6/Qt** umgestellt (statt komplettem Rewrite in z.B. TypeScript/Tauri) |
| DaVinci Resolve | **Nice-to-have, später** – kein Bestandteil des ersten v4.0.0-Release |
| Marker-Sync zu Premiere | **Batch-Sync-Button** nach der Show; lokale Datei bleibt während der Show alleinige verlässliche Quelle (kein Echtzeit-Push) |
| Zeitrahmen | Kein festes Datum – sauberes Vorgehen inkl. Feasibility-Spike hat Vorrang vor Tempo |
| Projekt-Speicherformat | **Eine Datei pro Projekt** (JSON, Vorschlag Endung `.qedl`), bei jeder Änderung atomar geschrieben – löst das bisherige Ordner+3-Textdateien-Modell ab |
| Marker-Farbe | Wird beim Erstellen **fest vom Markerlabel geerbt** und danach nicht mehr pro Marker einzeln geändert |
| Avid-Anbindung | Nur **Color-Set-Metadaten**, keine aktive Avid-Integration in dieser Roadmap geplant |

**Begründung Tech-Stack:** Beide Ziel-Integrationen sind herstellerseitig sprachlich festgelegt (UXP = JS-only, Resolve-Scripting = Python/Lua-only). Bei Python-Kern ist die Resolve-Anbindung nahezu kostenlos (nativer Import), während das UXP-Panel ohnehin als separates JS-Modul existieren muss – unabhängig von der Sprache der Haupt-App. Das minimiert Migrationsrisiko für einen Einzelmaintainer und erhält den Großteil der bestehenden Logik (Projekte, Settings, Playlist).

## Vorbereitung (erledigt in dieser Session)

- [x] `CLAUDE.md` angelegt (Architekturüberblick für zukünftige Agent-Sessions)
- [x] `deprecated/` entfernt (unreferenzierter Alt-Code: `settings_old.py`, `settings.yaml`)
- [x] Redundante CI-Workflows entfernt (`build_exe.yml`, `build_exe_sep-arch.yml` – älterer, undokumentierter Ansatz; `build-executables.yml` bleibt als aktueller, in `BUILD.md` dokumentierter Workflow)
- [x] Stray `.DS_Store` und `__pycache__` entfernt
- [x] `.gitignore`: `.claude/settings.local.json` ergänzt, toter `VSCode`-Eintrag entfernt
- [x] `dependencies.txt`: `pyyaml` (6.0.2→6.0.3) und `pyinstaller` (6.14.2→6.22.2) aktualisiert; `pillow` bleibt bei 10.4.0 (durch `ttkbootstrap`&nbsp;1.x hart auf `<11` begrenzt – das ist bereits die neueste kompatible Version); `ttkbootstrap` bewusst auf `<2.0.0` gepinnt (Major-Version mit Breaking Changes, GUI wird in Phase 1 ohnehin ersetzt statt migriert)

## Phase 0 – Machbarkeits-Spike (vor jeder Code-Entscheidung)

Höchstes Risiko und zentrale Motivation des gesamten Vorhabens zuerst validieren, bevor Aufwand in Phase 1 investiert wird.

**Code fertiggestellt, manueller Test steht noch aus:** siehe [`phase0-spike/`](phase0-spike/README.md) – ein lauffähiges UXP-Panel + lokaler Python-Server, direkt aus Adobes offiziellem Sample-Repo [`AdobeDocs/uxp-premiere-pro-samples`](https://github.com/AdobeDocs/uxp-premiere-pro-samples) abgeleitet. Der lokale Server-Teil ist bereits erfolgreich getestet (`curl`); der UXP-Panel-Teil erfordert eine laufende Premiere-Pro-GUI und damit einen manuellen Test durch dich – Details und Schritt-für-Schritt-Anleitung in `phase0-spike/README.md`.

**Wichtige Erkenntnis aus der Umsetzung:** Da wir Batch-Sync statt Echtzeit-Push gewählt haben, genügt ein einfacher `fetch`-Request statt einer dauerhaften WebSocket-Verbindung (einfacher als das ursprünglich als Referenz herangezogene `adb-mcp`-Muster) – die untenstehenden Punkte sind entsprechend angepasst.

- [x] Minimales UXP-Panel + lokaler Server bauen (`phase0-spike/`, Marker-API-Code direkt aus Adobes offiziellem Sample übernommen, nicht aus Sekundärquellen)
- [ ] Manuell verifizieren (siehe `phase0-spike/README.md`): Panel kann sich per `fetch` zu `http://localhost:8642` verbinden – Adobes eigenes OAuth-Sample (`sample-panels/oauth-workflow-sample`) nutzt exakt dieses Muster (`fetch`/XHR zu `http://localhost:8000`, `requiredPermissions.network.domains`), das reduziert das Risiko gegenüber der bisherigen Einschätzung spürbar
- [ ] Manuell verifizieren: Marker lassen sich über die UXP-API tatsächlich in der aktiven Sequenz anlegen (Button 1 im Spike-Panel)
- [ ] Manuell verifizieren: Marker-Farbe setzbar (`createSetColorByIndexAction`, Button 2) und vollständige Farbliste auslesen (`ppro.Constants.MarkerColor`, Button 3) – liefert die echten `export_string`-Werte fürs Premiere-Color-Set
- [ ] Mindestversion in der Praxis bestätigen: **widersprüchliche Angaben** – Adobes eigenes Sample-Manifest nennt `minVersion 25.1.0`/`25.2.0`, eine separate Quelle (Marker-Exporter-Plugin) nannte 25.6+. Gegen die tatsächlich installierte Premiere-Version prüfen (siehe offene Frage unten)
- [ ] `.ccx`-Packaging + Installation einmal end-to-end durchspielen (UDT → "Package" → Doppelklick-Install über Creative Cloud Desktop)
- [ ] Kurzes Entscheidungs-Memo: Architektur aus diesem Dokument bestätigen oder anpassen, bevor Phase 1 beginnt

## Phase 1 – Kern-Rewrite (Feature-Parität, neues GUI, noch ohne Premiere/Resolve)

Umgesetzt im Package `quickedl/` (parallel zum unangetasteten v3-Code, Start mit `python -m quickedl`). Kern und GUI sind mit Wegwerf-Skripten headless bzw. offscreen verifiziert – ein echtes Test-Setup fehlt noch (siehe offene Punkte am Ende der Phase).

### Projekt-Datei-Format & Speicherung
- [x] Neues Projekt-Format: **eine Datei pro Projekt** (JSON, Endung `.qedl`) statt Ordner mit drei Textdateien – kombiniert Marker-Liste, Playlist, Markerlabels und Projekt-Info in einer Struktur (`quickedl/core/project.py`, Details siehe [Feature-Konzept](#feature-konzept-projekt-datei-format))
- [x] Sicheres Schreiben: bei jeder Änderung **atomarer Rewrite** (Temp-Datei + `fsync` + `os.replace`), nie direktes In-Place-Überschreiben – ersetzt die ursprünglich für JSON-Lines vorgesehene Append-only-Strategie, behält aber deren Crash-Safety-Eigenschaft
- [x] Neue Projekt-Felder: `production_date`, `notes` (Freitext), `color_set`
- [x] Mitternachts-Bug behoben: Marker tragen volle ISO8601-Zeitstempel statt nur `HH:MM:SS`
- [x] TXT-Export-Funktion im v3-Zeilenformat inkl. 20-Zeichen-Trennlinie (`quickedl/core/export_txt.py`)
- [x] Migrations-Importer für v3.x-Projektordner (`quickedl/core/migration.py`), aufrufbar aus dem Projekt-Manager. Rekonstruiert zusätzlich die fehlenden Datumsangaben aus dem Änderungsdatum der EDL-Datei – inklusive Rückwärts-Rollover für Shows über Mitternacht

### Projekt-Manager (neues Fenster)
- [x] Liste aller bekannten Projekte (Registry in `quickedl/core/registry.py`); fehlende Dateien werden sichtbar als "nicht gefunden" markiert statt still zu verschwinden
- [x] Aktionen: Neues Projekt, Öffnen, Vorhandene Datei hinzufügen, Umbenennen (Projektname + Dateiname synchron), "Aus Liste entfernen" vs. "Datei löschen" (letzteres mit Rückfrage)
- [x] Import/Konvertierung alter v3.x-Projekte
- [x] Anzeige von Produktionsdatum und Änderungsdatum in der Liste

### Color-Sets & Marker-Farben
- [x] Color-Set-Datenformat als separate Dateien (`quickedl/colorsets/*.json`)
- [x] Eingebaute Color-Sets: Premiere Pro, DaVinci Resolve, Avid Media Composer
- [x] Custom-Color-Sets aus `~/quickedl/v4/colorsets/` werden geladen und überschreiben gleichnamige eingebaute Sets. Grafischer Color-Set-Editor bleibt spätere Ausbaustufe
- [x] Color-Set wird pro Projekt bei Erstellung festgelegt und ist danach nicht mehr wechselbar (in den Projekt-Einstellungen nur lesend angezeigt)
- [x] Markerlabels haben je eine Farbe aus dem Color-Set (Farbauswahl-Button neben jedem Label-Feld)
- [x] Marker erben die Label-Farbe **zum Erstellungszeitpunkt** fest; spätere Label-Farbänderungen wirken nicht rückwirkend
- [x] Projekt-Settings: eigene Default-Farbe für Popup- und Playlist-Marker
- [ ] **Offen:** die `export_string`-Werte aller drei Sets sind unverifizierte Platzhalter (im JSON per `"export_strings_verified": false` markiert). Echte Werte kommen aus dem Phase-0-Test (Button 3 liest `ppro.Constants.MarkerColor` aus)

### GUI-Neuaufbau (PySide6/Qt)
- [x] Feature-Parität zum bisherigen Funktionsumfang:
  - [x] Projekt-Verwaltung über den neuen Projekt-Manager
  - [x] Schmale nummerierte Marker-Buttons (1–9) mit separatem Label-Feld und Farbauswahl
  - [x] Hotkeys 1–9, 0, Leertaste, P, ←/→, Backspace über einen anwendungsweiten Event-Filter (`keyPressEvent` reicht nicht: fokussierte Buttons und Textfelder fangen die Tasten vorher ab). Alle Aktions-Buttons sind auf `Qt.NoFocus` gesetzt, damit die Leertaste nicht den fokussierten Button auslöst
  - [x] Hotkey-Indikator in der Statusleiste (grün „Hotkeys aktiv" / grau mit Grund: kein Projekt, Dialog offen, Fenster nicht aktiv, Texteingabe) – analog zum Indikator der v3-GUI. Escape verlässt ein Label-Feld und aktiviert die Hotkeys wieder
  - [x] Trennlinie (Taste 0)
  - [x] Popup-Marker mit Freitext (Leertaste) – Zeitstempel wird beim Öffnen des Dialogs genommen, nicht beim Bestätigen
  - [x] Playlist-Marker (P) mit Auto-Advance und Pfeiltasten-Navigation
  - [x] Letzten Marker löschen (Backspace, standardmäßig deaktiviert)
  - [x] Auto-Save entfällt als eigenes Feature: jede Änderung wird sofort atomar geschrieben
  - [x] Einstellungs-Fenster (YAML unter `~/quickedl/v4/`)
- [x] Modernes visuelles Redesign (dunkles, kompaktes Qt-Stylesheet, `quickedl/gui/style.py`); Marker-Farben werden in der Marker-Liste als Farbstreifen dargestellt

### Offene Punkte dieser Phase
- [ ] Echtes Test-Setup statt Wegwerf-Skripten (der Kern ist rein logisch und gut testbar – pytest wäre naheliegend)
- [ ] Manueller Praxistest der GUI durch dich (automatisiert bisher nur offscreen geprüft; die Offscreen-Plattform kennt keine echte Fenster-Aktivierung, daher ist der Indikator-Zustand „Fenster nicht aktiv" nur manuell prüfbar)
- [ ] Vor Release: v4-Benutzerdaten von `~/quickedl/v4/` nach `~/quickedl/` hochziehen und v3-Dateien entfernen

### Packaging
- [ ] CI/Packaging für PySide6 neu aufsetzen (bestehendes `quickedl.spec`/`build.py`-Muster als Ausgangspunkt, PySide6-spezifische PyInstaller-Hooks berücksichtigen)
- [ ] Linux als offizielle Zielplattform entscheiden und ggf. in CI-Matrix ergänzen (siehe offene Frage)
- [ ] `version.py` auf 4.0.0 (bzw. `4.0.0-dev`) aktualisieren, sobald Feature-Parität erreicht ist

## Phase 2 – Premiere Pro UXP-Integration

- [ ] Lokaler HTTP-Server in der Haupt-App (liefert ausstehende Marker auf Anfrage – kein WebSocket nötig, siehe Phase-0-Erkenntnis: Batch-Sync statt Echtzeit-Push macht eine dauerhafte Verbindung überflüssig; Prototyp in `phase0-spike/local-server/server.py`)
- [ ] UXP-Companion-Panel (JS), holt sich per `fetch` die Marker vom lokalen Server, erstellt sie in der aktiven Sequenz (Prototyp in `phase0-spike/uxp-panel/`)
- [ ] JSON-Protokoll zwischen App und Panel definieren (marker id, timecode-Offset, label, type, Farbe)
- [ ] Marker-Farbe beim Export mitgeben: `export_string` des Color-Set-Eintrags an die UXP-Marker-API übergeben (genaues Premiere-Farb-Vokabular/API in Phase 0/2 gegen die reale UXP-Dokumentation verifizieren – im Color-Set-Konzept aktuell nur Platzhalter-Werte)
- [ ] Batch-"Sync"-Button in der GUI (siehe Architektur-Entscheidung oben – kein automatischer Echtzeit-Push)
- [ ] Distribution des Panels: `.ccx`-Paket über GitHub-Releases bündeln; einmaliger manueller Doppelklick-Install (Minimalversion) vs. automatischer Install über eigenen Installer via **UPIA**-CLI (Komfort-Ausbaustufe, siehe offene Frage)
- [ ] Bestehenden JSX/ExtendScript-Export **als dauerhaften Fallback** für Premiere < 25.6 erhalten und in der neuen GUI weiter zugänglich machen
- [ ] Dokumentation analog zu `docs/jsx.md` für den neuen UXP-Workflow

## Phase 3 – Optionale DaVinci-Resolve-Integration

- [ ] Anbindung über `DaVinciResolveScript`-Modul (nativer Python-Import, kein Bridge-Prozess nötig)
- [ ] "External Scripting" Voraussetzungen dokumentieren (Resolve-Einstellung, `RESOLVE_SCRIPT_API`/`RESOLVE_SCRIPT_LIB`/`PYTHONPATH`)
- [ ] Frame-basierte Marker-API berücksichtigen (`timeline.AddMarker(frameId, color, name, note, duration, customData)`) – eigene FPS-Offset-Berechnung nötig (analog zur heutigen JSX-Sekundenberechnung, nur frame-genau)
- [ ] Gleiches strukturiertes Marker-Modell aus Phase 1 wiederverwenden, sodass Resolve "nur ein weiterer Marker-Consumer" ist, symmetrisch zum UXP-Panel
- [ ] Color-Set-`export_string` direkt als `color`-Parameter an `AddMarker` übergeben (Resolve nutzt bereits benannte Farb-Strings – Werte im DaVinci-Color-Set müssen mit Resolves tatsächlichem Namensvokabular abgeglichen werden, siehe Platzhalter im Color-Set-Konzept)

## Feature-Konzept: Projekt-Datei-Format

Ersetzt das bisherige Modell "Ordner + `_EDL.txt` + `_MARKERLABEL.txt` + `_PLAYLIST.txt`" durch eine einzelne Datei pro Projekt. Vorschlag: JSON mit eigener Endung `.qedl`, damit Projekte im Dateisystem als ein zusammengehöriges, doppelklickbares Objekt erkennbar sind (Endung/Name frei anpassbar).

```jsonc
{
  "format_version": 1,
  "project": {
    "name": "Show XY",
    "production_date": "2026-08-26",
    "notes": "Freitext-Notizen zum Projekt",
    "color_set": "premiere_pro",              // Referenz auf ein Color-Set (siehe unten)
    "default_popup_marker_color": "red",      // Projekt-Setting, siehe Color-Set-Konzept
    "default_playlist_marker_color": "blue",
    "created_at": "2026-08-20T09:00:00",
    "modified_at": "2026-08-26T20:15:03"
  },
  "marker_labels": [
    { "index": 1, "label": "Take", "color": "red" },
    { "index": 2, "label": "Cut",  "color": null }
  ],
  "playlist": [
    { "label": "Song 1" },
    { "label": "Song 2" }
  ],
  "markers": [
    { "id": "uuid", "created_at": "2026-08-26T20:15:03", "type": "label",     "source_label_index": 1, "label": "Take",         "color": "red" },
    { "id": "uuid", "created_at": "2026-08-26T20:16:10", "type": "popup",     "label": "Freitext",     "color": "blue" },
    { "id": "uuid", "created_at": "2026-08-26T20:17:00", "type": "separator" }
  ]
}
```

**Schreibstrategie:** Bei jeder Änderung wird die komplette Datei in `<name>.qedl.tmp` geschrieben und danach per `os.replace()` atomar an die Stelle der bisherigen Datei verschoben. Die Originaldatei wird nie direkt verändert – bei einem Absturz während des Schreibens bleibt der zuletzt vollständig gespeicherte Stand erhalten. Separator-Zeilen bekommen keine Farbe (sie werden schon heute nicht als Marker exportiert, siehe `export_jsx.py`).

## Feature-Konzept: Projekt-Manager

Neues, eigenständiges Fenster, das die heutige verstreute Ordner-Logik (Menüpunkte "Neu/Laden/Zuletzt verwendet") durch eine zentrale Übersicht ersetzt:

- **Liste**: alle bekannten Projekte (Registry aus Pfaden, erweitert aus der heutigen `settings/recent.py`-Logik), mit Name, Produktionsdatum, letzter Änderung; fehlt eine Datei am gespeicherten Pfad (verschoben/gelöscht), wird der Eintrag sichtbar als "nicht gefunden" markiert statt kommentarlos zu verschwinden
- **Neu**: legt eine neue `.qedl`-Datei an einem wählbaren Ort an
- **Umbenennen**: ändert `project.name` und den Dateinamen zusammen
- **Löschen**: mit Rückfrage, getrennt in "aus Liste entfernen" (Datei bleibt erhalten) und "Datei endgültig löschen"
- **Import**: wählt einen alten v3.x-Projektordner, konvertiert ihn in eine neue `.qedl`-Datei (fehlende neue Felder wie Produktionsdatum/Notizen/Color-Set werden beim Import leer bzw. mit einem Default-Color-Set vorbelegt und können direkt angepasst werden)

## Feature-Konzept: Color-Sets

Color-Sets sind eigenständige Dateien (kein hartcodiertes Enum im Programmcode), damit neue Schnittprogramme oder eigene Paletten ergänzt werden können, ohne den Kern der App zu ändern. Eingebaute Sets liegen als Ressourcen im Repo (z.B. `colorsets/*.json`), nutzerdefinierte "Custom"-Sets im Settings-Ordner (`~/quickedl/colorsets/`).

```jsonc
{
  "id": "davinci_resolve",
  "name": "DaVinci Resolve",
  "colors": [
    { "label": "Blau",   "display_color": "#3B5EA8", "export_string": "Blue" },
    { "label": "Rot",    "display_color": "#C0392B", "export_string": "Red" },
    { "label": "Grün",   "display_color": "#4E9A51", "export_string": "Green" },
    { "label": "Gelb",   "display_color": "#E5C22D", "export_string": "Yellow" }
  ]
}
```

- `label`: Anzeigename in der QuickEDL-UI (frei wählbar, z.B. auch "Wichtig" statt Farbname)
- `display_color`: Hex-Code, mit dem QuickEDL selbst die Farbe rendert
- `export_string`: exakter Bezeichner, den die Ziel-Anwendung beim Marker-Import erwartet

**Geplante Sets zum Start:** Premiere Pro, DaVinci Resolve, Avid Media Composer (nur Metadaten/keine aktive Anbindung, s.o.), Custom (nutzerdefiniert). Die `export_string`-Werte für Premiere und Avid sind noch **nicht verifiziert** (in obigem Beispiel bewusst nur für Resolve grob skizziert, da dessen `AddMarker`-API bereits benannte Farb-Strings verwendet) – die tatsächlichen Werte müssen bei Umsetzung von Phase 2 (Premiere-UXP-API) bzw. bei einer möglichen späteren Avid-Arbeit recherchiert und gegen die jeweilige Dokumentation/Version abgeglichen werden. Bis dahin sind die Sets Platzhalter mit plausibler Struktur, nicht garantiert korrekten Werten.

## Offene Fragen

Diese Punkte sollten geklärt werden (bzw. sind bewusst nachrangig), bevor die jeweils betroffene Phase beginnt:

1. **Premiere-Versionen im tatsächlichen Einsatz**: Reicht die Annahme "meist aktuell/UXP-fähig", oder muss der JSX-Fallback für einen relevanten Nutzeranteil erstklassig (nicht nur Notlösung) bleiben? Relevant für Phase 2.
2. **Linux offiziell unterstützen?** Es gibt bereits ein totes Indiz dafür in der Vergangenheit (ein `resources/icon_unix.png` sowie – jetzt entfernte – alte Workflow-Dateien, die tatsächlich einen Unix-Build erzeugten). Beeinflusst die CI-Planung in Phase 1.
3. **Panel-Installation**: Reicht ein einmaliger manueller `.ccx`-Doppelklick (einfachste Variante, ähnlich dem heutigen VS-Code-Setup), oder soll QuickEDL das Panel über UPIA automatisch mitinstallieren? Relevant für Phase 2.
4. **Mehrplatz-/Sync-Interesse**: Besteht Interesse an späterem Teilen/Synchronisieren von Projektdaten über mehrere Maschinen/Operatoren hinweg? Würde die konservative Einzeldatei-Architektur ggf. in Frage stellen.
5. **Branch `struct-data-concept`**: Existiert (0 Commits gegenüber `main`, aktuell leerer Platzhalter) – steckt dahinter bereits Vordenken zum Datenmodell, das eingearbeitet werden sollte, oder kann er verworfen werden?
6. **Farbauswahl-UI**: Soll die Farbe je Markerlabel direkt inline gewählt werden (z.B. Farb-Swatch-Button neben jedem Label-Feld), oder über einen separaten Dialog? Kleinere UI-Detailfrage für Phase 1.
7. **Dateiendung für Projekt-Dateien**: Vorschlag `.qedl` (siehe Feature-Konzept) – passt das, oder lieber `.json` bzw. ein anderer Name?

## Referenzen aus der Recherche

- [Premiere API — UXP for Adobe Premiere](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/)
- [UXP Premiere Pro Network Recipe](https://developer.adobe.com/premiere-pro/uxp/resources/recipes/network)
- [Install a UXP plugin](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/install/)
- [Distribution Overview](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/overview)
- [Package a UXP plugin](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/package)
- [Enterprise Distribution / UPIA](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/enterprise-distribution)
- [mikechambers/adb-mcp – ursprüngliche Referenzarchitektur für UXP↔lokaler-App-Kommunikation (WebSocket-basiert; für unseren Batch-Sync-Anwendungsfall inzwischen durch das einfachere `fetch`-Muster aus Adobes eigenem OAuth-Sample ersetzt)](https://github.com/mikechambers/adb-mcp)
- [AdobeDocs/uxp-premiere-pro-samples – offizielle Adobe-Samples, Quelle für den Phase-0-Spike-Code (Marker-API, Netzwerk-Manifest, Panel-Grundstruktur)](https://github.com/AdobeDocs/uxp-premiere-pro-samples)
- [Marker Exporter for Premiere Pro (Adobe Exchange) – Praxisbeleg für UXP-Marker-API, kompatibel ab Premiere 25.6](https://exchange.adobe.com/apps/cc/edd8fa87/marker-exporter-for-premiere-pro)
