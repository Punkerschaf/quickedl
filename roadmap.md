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

- [ ] Minimales UXP-Panel gegen die tatsächlich genutzte(n) Premiere-Pro-Version(en) bauen (Referenzarchitektur: [mikechambers/adb-mcp](https://github.com/mikechambers/adb-mcp) – Panel verbindet sich per WebSocket zu `http://localhost:PORT`)
- [ ] Verifizieren: Panel kann sich zu einem lokalen WebSocket/HTTP-Server verbinden (Manifest-Permission `requiredPermissions.network.domains` inkl. `http://localhost:<port>`)
- [ ] Verifizieren: `http://localhost` funktioniert unter macOS trotz grundsätzlicher HTTPS-Restriktion für `fetch` (adb-mcp legt das nahe, ist aber nicht offiziell dokumentiert)
- [ ] Verifizieren: Marker lassen sich über die UXP-API tatsächlich in der aktiven Sequenz anlegen
- [ ] Mindestversion in der Praxis bestätigen: offiziell **Premiere v25.6+, UDT v2.2, Manifest v5** – prüfen, ob das mit den tatsächlichen Zielumgebungen kompatibel ist (siehe offene Frage unten)
- [ ] `.ccx`-Packaging + Installation einmal end-to-end durchspielen (UDT → "Package" → Doppelklick-Install über Creative Cloud Desktop)
- [ ] Kurzes Entscheidungs-Memo: Architektur aus diesem Dokument bestätigen oder anpassen, bevor Phase 1 beginnt

## Phase 1 – Kern-Rewrite (Feature-Parität, neues GUI, noch ohne Premiere/Resolve)

- [ ] Neues Datenmodell: Append-only **JSON-Lines** (`.jsonl`) als Source of Truth pro Projekt (Felder mind. `id`, `created_at` als volles ISO8601-Datetime, `label`, `type`); behebt den bestehenden Mitternachts-Bug (aktuell nur `HH:MM:SS` ohne Datum)
- [ ] Klartext-`.txt`-EDL bleibt als Export-/Backup-Format erhalten (Lesbarkeit während der Show ist eine bewusste Eigenschaft des aktuellen Designs)
- [ ] Migrations-Importer für bestehende `_EDL.txt`-Projektordner (Parsing-Logik aus `export_jsx.py::get_edl_markers` / `main.py` wiederverwenden)
- [ ] GUI-Neuaufbau in PySide6/Qt mit Feature-Parität zum aktuellen Funktionsumfang:
  - [ ] Projekt-Verwaltung (Neu/Laden/Zuletzt verwendet)
  - [ ] Marker-Buttons mit editierbaren Labels + Hotkeys 1–9
  - [ ] Separator (Taste 0)
  - [ ] Popup-Marker mit Freitext (Space)
  - [ ] Playlist-Marker (P, Pfeiltasten-Navigation)
  - [ ] Letzten Marker löschen (Backspace, standardmäßig deaktiviert)
  - [ ] Auto-Save
  - [ ] Settings-Fenster (YAML-Speicherort ggf. beibehalten: `~/quickedl/`)
- [ ] Modernes visuelles Redesign (Look & Feel, Theming über Qt-Stylesheets/qt-material o.ä.)
- [ ] CI/Packaging für PySide6 neu aufsetzen (bestehendes `quickedl.spec`/`build.py`-Muster als Ausgangspunkt, PySide6-spezifische PyInstaller-Hooks berücksichtigen)
- [ ] Linux als offizielle Zielplattform entscheiden und ggf. in CI-Matrix ergänzen (siehe offene Frage)
- [ ] `version.py` auf 4.0.0 (bzw. `4.0.0-dev`) aktualisieren, sobald Feature-Parität erreicht ist

## Phase 2 – Premiere Pro UXP-Integration

- [ ] Lokaler WebSocket/HTTP-Server in der Haupt-App (Marker-Events bereitstellen)
- [ ] UXP-Companion-Panel (JS), verbindet sich zum lokalen Server, erstellt Marker in der aktiven Sequenz
- [ ] JSON-Protokoll zwischen App und Panel definieren (marker id, timecode-Offset, label, type)
- [ ] Batch-"Sync"-Button in der GUI (siehe Architektur-Entscheidung oben – kein automatischer Echtzeit-Push)
- [ ] Distribution des Panels: `.ccx`-Paket über GitHub-Releases bündeln; einmaliger manueller Doppelklick-Install (Minimalversion) vs. automatischer Install über eigenen Installer via **UPIA**-CLI (Komfort-Ausbaustufe, siehe offene Frage)
- [ ] Bestehenden JSX/ExtendScript-Export **als dauerhaften Fallback** für Premiere < 25.6 erhalten und in der neuen GUI weiter zugänglich machen
- [ ] Dokumentation analog zu `docs/jsx.md` für den neuen UXP-Workflow

## Phase 3 – Optionale DaVinci-Resolve-Integration

- [ ] Anbindung über `DaVinciResolveScript`-Modul (nativer Python-Import, kein Bridge-Prozess nötig)
- [ ] "External Scripting" Voraussetzungen dokumentieren (Resolve-Einstellung, `RESOLVE_SCRIPT_API`/`RESOLVE_SCRIPT_LIB`/`PYTHONPATH`)
- [ ] Frame-basierte Marker-API berücksichtigen (`timeline.AddMarker(frameId, color, name, note, duration, customData)`) – eigene FPS-Offset-Berechnung nötig (analog zur heutigen JSX-Sekundenberechnung, nur frame-genau)
- [ ] Gleiches strukturiertes Marker-Modell aus Phase 1 wiederverwenden, sodass Resolve "nur ein weiterer Marker-Consumer" ist, symmetrisch zum UXP-Panel

## Offene Fragen

Diese Punkte sollten geklärt werden (bzw. sind bewusst nachrangig), bevor die jeweils betroffene Phase beginnt:

1. **Premiere-Versionen im tatsächlichen Einsatz**: Reicht die Annahme "meist aktuell/UXP-fähig", oder muss der JSX-Fallback für einen relevanten Nutzeranteil erstklassig (nicht nur Notlösung) bleiben? Relevant für Phase 2.
2. **Linux offiziell unterstützen?** Es gibt bereits ein totes Indiz dafür in der Vergangenheit (ein `resources/icon_unix.png` sowie – jetzt entfernte – alte Workflow-Dateien, die tatsächlich einen Unix-Build erzeugten). Beeinflusst die CI-Planung in Phase 1.
3. **Panel-Installation**: Reicht ein einmaliger manueller `.ccx`-Doppelklick (einfachste Variante, ähnlich dem heutigen VS-Code-Setup), oder soll QuickEDL das Panel über UPIA automatisch mitinstallieren? Relevant für Phase 2.
4. **Marker-Typ-Klassifizierung**: Soll jeder Marker/jede Zeile im neuen GUI einen expliziten Typ bekommen (für sauberen NLE-Export), oder bleibt das wie heute implizit? Relevant für Phase 1 Datenmodell.
5. **Mehrplatz-/Sync-Interesse**: Besteht Interesse an späterem Teilen/Synchronisieren von Projektdaten über mehrere Maschinen/Operatoren hinweg? Würde die konservative Einzeldatei-JSONL-Architektur ggf. in Frage stellen.
6. **Branch `struct-data-concept`**: Existiert (0 Commits gegenüber `main`, aktuell leerer Platzhalter) – steckt dahinter bereits Vordenken zum Datenmodell, das eingearbeitet werden sollte, oder kann er verworfen werden?

## Referenzen aus der Recherche

- [Premiere API — UXP for Adobe Premiere](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/)
- [UXP Premiere Pro Network Recipe](https://developer.adobe.com/premiere-pro/uxp/resources/recipes/network)
- [Install a UXP plugin](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/install/)
- [Distribution Overview](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/overview)
- [Package a UXP plugin](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/package)
- [Enterprise Distribution / UPIA](https://developer.adobe.com/premiere-pro/uxp/plugins/distribution/enterprise-distribution)
- [mikechambers/adb-mcp – Referenzarchitektur für UXP↔lokaler-App-Kommunikation](https://github.com/mikechambers/adb-mcp)
- [Marker Exporter for Premiere Pro (Adobe Exchange) – Praxisbeleg für UXP-Marker-API, kompatibel ab Premiere 25.6](https://exchange.adobe.com/apps/cc/edd8fa87/marker-exporter-for-premiere-pro)
