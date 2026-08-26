// QuickEDL Phase 0 Spike – Panel logic.
// Marker API usage adapted from Adobe's official sample:
// https://github.com/AdobeDocs/uxp-premiere-pro-samples (sample-panels/premiere-api/src/markers.ts)

const ppro = require("premierepro");

const SERVER_URL = "http://localhost:8642";

function log(message, color) {
  const el = document.getElementById("log");
  const line = document.createElement("div");
  if (color) line.style.color = color;
  line.textContent = message;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
  console.log(message);
}

async function getActiveContext() {
  const project = await ppro.Project.getActiveProject();
  if (!project) {
    log("Kein aktives Projekt in Premiere gefunden.", "red");
    return null;
  }
  const sequence = await project.getActiveSequence();
  if (!sequence) {
    log("Keine aktive Sequenz gefunden. Bitte eine Sequenz im Timeline-Panel öffnen.", "red");
    return null;
  }
  return { project, sequence };
}

async function createTestMarker(label = "QuickEDL Test", seconds = 0) {
  const ctx = await getActiveContext();
  if (!ctx) return false;
  const { project, sequence } = ctx;

  try {
    const sequenceMarkers = await ppro.Markers.getMarkers(sequence);
    let success = false;
    project.lockedAccess(() => {
      success = project.executeTransaction((compoundAction) => {
        const addMarkerAction = sequenceMarkers.createAddMarkerAction(
          label,
          ppro.Marker.MARKER_TYPE_COMMENT,
          ppro.TickTime.createWithSeconds(seconds),
          ppro.TickTime.TIME_ZERO,
          "Erstellt vom QuickEDL Phase-0-Spike"
        );
        compoundAction.addAction(addMarkerAction);
      }, "QuickEDL Spike: Create Marker");
    });
    log(`Marker "${label}" bei ${seconds}s erstellt: ${success}`, success ? "lightgreen" : "red");
    return success;
  } catch (err) {
    log(`Fehler beim Erstellen des Markers: ${err}`, "red");
    return false;
  }
}

async function setFirstMarkerColorBlue() {
  const ctx = await getActiveContext();
  if (!ctx) return false;
  const { project, sequence } = ctx;

  try {
    const sequenceMarkersOwner = await ppro.Markers.getMarkers(sequence);
    const markers = sequenceMarkersOwner.getMarkers();
    if (markers.length === 0) {
      log("Keine Marker in der Sequenz gefunden – zuerst Test-Marker erstellen (Button 1).", "orange");
      return false;
    }
    const firstMarker = markers[0];
    let success = false;
    project.lockedAccess(() => {
      success = project.executeTransaction((compoundAction) => {
        const setColorAction = firstMarker.createSetColorByIndexAction(ppro.Constants.MarkerColor.BLUE);
        compoundAction.addAction(setColorAction);
      }, "QuickEDL Spike: Set Marker Color");
    });
    log(`Farbe des ersten Markers auf BLUE gesetzt: ${success}`, success ? "lightgreen" : "red");
    return success;
  } catch (err) {
    log(`Fehler beim Setzen der Marker-Farbe: ${err}`, "red");
    return false;
  }
}

function logAvailableColors() {
  // Ziel: das vollstaendige Farb-Set fuer das Color-Set-Konzept (export_string je Farbe) ermitteln.
  try {
    const colors = ppro.Constants.MarkerColor;
    log(`ppro.Constants.MarkerColor = ${JSON.stringify(colors)}`);
  } catch (err) {
    log(`Fehler beim Auslesen der Farb-Konstanten: ${err}`, "red");
  }
}

async function syncFromServer() {
  document.getElementById("status").textContent = `Verbinde zu ${SERVER_URL} ...`;
  try {
    const response = await fetch(`${SERVER_URL}/pending-markers`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const markers = await response.json();
    log(`${markers.length} Marker vom QuickEDL-Server erhalten.`, "lightgreen");
    document.getElementById("status").textContent =
      `Verbunden mit ${SERVER_URL}. Synchronisiere ${markers.length} Marker ...`;

    for (const marker of markers) {
      await createTestMarker(marker.label, marker.seconds);
    }
    document.getElementById("status").textContent = `Sync abgeschlossen: ${markers.length} Marker.`;
  } catch (err) {
    log(`Fehler beim Verbinden zu ${SERVER_URL}: ${err}`, "red");
    document.getElementById("status").textContent =
      "Verbindung fehlgeschlagen. Laeuft der lokale Server (local-server/server.py)?";
  }
}

document.getElementById("btn-marker").onclick = () => createTestMarker("QuickEDL Test-Marker", 0);
document.getElementById("btn-color").onclick = () => setFirstMarkerColorBlue();
document.getElementById("btn-colors").onclick = () => logAvailableColors();
document.getElementById("btn-sync").onclick = () => syncFromServer();

log("Panel geladen. Bereit fuer Phase-0-Tests.");
