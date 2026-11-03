import json
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler

from ..config import TEMPLATES_DIR, STATIC_DIR
from ..database import get_all_listings, create_listing
from ..services.sarvam_service import analyze_study_material_image

class MarketplaceHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests for PICT Campus Marketplace."""

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        # Serve main HTML application
        if self.path in ("/", "/index.html"):
            index_path = TEMPLATES_DIR / "index.html"
            if index_path.exists():
                content = index_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(500, "Template index.html not found")

        # API: Get all listings
        elif self.path == "/api/listings":
            try:
                listings = get_all_listings()
                self._send_json({"listings": listings})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        # Serve static assets from /static/
        elif self.path.startswith("/static/"):
            rel_path = self.path[len("/static/"):]
            static_file = STATIC_DIR / rel_path
            if static_file.exists() and static_file.is_file():
                mime, _ = mimetypes.guess_type(str(static_file))
                mime = mime or "application/octet-stream"
                content = static_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Static file not found")

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length)
        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        # API: AI Vision analysis of study material
        if self.path == "/api/analyze":
            data_uri = payload.get("image_data_uri")
            if not data_uri:
                self._send_json({"error": "image_data_uri is required"}, status=400)
                return
            try:
                analysis = analyze_study_material_image(data_uri)
                self._send_json({"success": True, "analysis": analysis})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        # API: Create new listing
        elif self.path == "/api/listings":
            try:
                new_id = create_listing(payload)
                self._send_json({"success": True, "id": new_id})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Not Found")

