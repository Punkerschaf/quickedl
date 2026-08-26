# Phase 0 – Machbarkeits-Spike: Premiere Pro UXP

Ziel: end-to-end verifizieren, dass ein UXP-Panel (a) Marker in einer laufenden Premiere-Pro-Sequenz erstellen kann, (b) deren Farbe setzen kann, und (c) sich dafür per `fetch` zu einem lokalen HTTP-Server verbinden kann – bevor Aufwand in Phase 1 investiert wird (siehe `roadmap.md`).

Dieser Test erfordert eine laufende Adobe-Premiere-Pro-GUI und ist daher **manuell durchzuführen** – das kann ich als CLI-Agent nicht selbst ausführen.

## Was hier liegt

- `uxp-panel/` – minimales UXP-Plugin (Manifest + reines HTML/JS, kein Build-Schritt nötig). Code-Muster 1:1 aus Adobes offiziellem Sample-Repo [`AdobeDocs/uxp-premiere-pro-samples`](https://github.com/AdobeDocs/uxp-premiere-pro-samples) übernommen (`sample-panels/premiere-api/src/markers.ts` für die Marker-API, `sample-panels/oauth-workflow-sample` für das `fetch`-zu-`localhost`-Muster).
- `local-server/server.py` – minimaler lokaler HTTP-Server (nur Python-Standardbibliothek), simuliert die Rolle der späteren QuickEDL-App. Wurde bereits lokal getestet (`GET /pending-markers` liefert die drei Platzhalter-Marker, `curl`-verifiziert).

**Wichtige Design-Entscheidung, die dieser Spike widerspiegelt:** Da wir uns für Batch-Sync statt Echtzeit-Push entschieden haben (siehe `roadmap.md`), reicht ein einfacher `fetch`-Request beim Klick auf "Sync" – keine dauerhafte WebSocket-Verbindung nötig. Das ist einfacher als das ursprünglich als Referenz herangezogene `adb-mcp`-Muster.

## Voraussetzungen

- Adobe Premiere Pro, aktuelle Version (offiziell mindestens 25.1–25.6, siehe Hinweis unten)
- [Adobe UXP Developer Tool (UDT)](https://developer.adobe.com/creative-cloud/uxp-developer-tools/) installiert
- Creative Cloud Desktop läuft
- Ein Premiere-Projekt mit einer geöffneten, aktiven Sequenz in der Timeline

## Schritte

1. **Server starten:**
   ```bash
   cd phase0-spike/local-server
   python3 server.py
   ```
   Sollte `QuickEDL Phase-0-Spike-Server laeuft auf http://localhost:8642` ausgeben.

2. **Plugin in UDT laden:**
   - UDT öffnen → "Add Plugin" → `phase0-spike/uxp-panel/manifest.json` auswählen
   - Plugin in der Liste anklicken → "Load" (Premiere Pro muss dabei bereits laufen)
   - Falls UDT wegen fehlender Icons meckert: kann ignoriert werden oder Icons nachträglich im Manifest ergänzen – für den Test irrelevant.

3. **Panel in Premiere öffnen:** `Window > UXP Plugins > QuickEDL Spike`

4. **Buttons der Reihe nach testen** (Ergebnisse erscheinen im Log-Bereich des Panels):
   - **1. Test-Marker erstellen** → prüfen, ob in der Timeline bei 0s tatsächlich ein Marker erscheint
   - **2. Marker-Farbe setzen (Blue)** → prüfen, ob der erste Marker in der Timeline blau wird
   - **3. Verfügbare Marker-Farben loggen** → Log-Ausgabe von `ppro.Constants.MarkerColor` notieren (liefert die vollständige Farbliste für das Color-Set-Konzept in `roadmap.md`)
   - **4. Von QuickEDL-Server synchronisieren** → prüft `fetch` zu `http://localhost:8642` UND legt die 3 Platzhalter-Marker aus dem Server in der Sequenz an

5. **Ergebnisse zurück in `roadmap.md` eintragen** (Phase-0-Checkliste abhaken, insbesondere die tatsächliche Mindestversion und ob localhost/HTTPS auf macOS Probleme gemacht hat).

## Bekannte offene Punkte / Unsicherheiten in diesem Code

- **Mindestversion widersprüchlich:** Adobes eigenes Sample-Manifest nennt `minVersion: 25.1.0` bzw. `25.2.0` für Marker- und Netzwerk-Features; eine früher separat gefundene Quelle (Adobe-Exchange-Plugin "Marker Exporter") nannte **25.6+**. Dieser Spike nutzt `25.1.0` – bitte gegen die tatsächlich installierte Premiere-Version prüfen und in `roadmap.md` festhalten, welche Version real funktioniert hat.
- **`requiredPermissions.network.domains: "all"`** ist für den Spike bewusst maximal permissiv gewählt (spart Debugging von Domain-Syntax). Für die echte Phase-2-Implementierung sollte das auf `http://localhost:<port>` eingeschränkt werden (Least Privilege).
- **Marker-Typ:** Der Spike nutzt `MARKER_TYPE_COMMENT`. Ob das für QuickEDLs Zwecke der richtige Typ ist (vs. Chapter/Weblink) sollte in Phase 2 nochmal bewusst entschieden werden.
- **Icons fehlen im Manifest** – für den Funktionstest irrelevant, für eine spätere echte Distribution nachzuholen.
