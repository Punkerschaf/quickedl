"""
Minimaler lokaler HTTP-Server fuer den Phase-0-Spike.

Simuliert die Rolle, die spaeter die echte QuickEDL-App einnimmt: er haelt
eine kleine Liste "ausstehender" Marker vor und liefert sie auf Anfrage des
UXP-Panels aus (Batch-Sync statt Echtzeit-Push, siehe roadmap.md).

Nutzt bewusst nur die Python-Standardbibliothek (http.server) -- fuer den
Spike soll keine zusaetzliche Abhaengigkeit noetig sein.

Start: python3 server.py
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8642

# Platzhalter-Marker, wie sie spaeter aus einer echten .qedl-Projektdatei kommen wuerden.
PENDING_MARKERS = [
    {"label": "QuickEDL Spike Marker 1", "seconds": 0},
    {"label": "QuickEDL Spike Marker 2", "seconds": 5},
    {"label": "QuickEDL Spike Marker 3", "seconds": 12},
]


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        # Permissive CORS-Header, falls UXP den Request wie ein Browser-fetch behandelt.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/pending-markers":
            self._send_json(PENDING_MARKERS)
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[server] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    httpd = HTTPServer(("localhost", PORT), Handler)
    print(f"QuickEDL Phase-0-Spike-Server laeuft auf http://localhost:{PORT}")
    print("Endpunkt: GET /pending-markers")
    print("Zum Beenden: Strg+C")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
