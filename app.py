"""
PICT Campus Marketplace (OLX for PICT)
--------------------------------------
A study material marketplace for PICT students.
Powered by Sarvam AI Vision (gemma4).

Usage:
  python app.py                   # Starts the web app at http://localhost:8000/
  python app.py --test            # Verifies connection to Sarvam AI API
  python app.py --cli <img_path>  # Scans an image and outputs structured JSON
"""

import sys
import json
import base64
import socket
import mimetypes
from pathlib import Path
from http.server import HTTPServer

from src.config import PORT, STATIC_DIR
from src.database import init_db
from src.handlers.http_handler import MarketplaceHandler
from src.services.sarvam_service import analyze_study_material_image, test_connection

def run_server(port: int = PORT):
    """Starts the HTTP server and prints accessible URLs."""
    init_db()
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, MarketplaceHandler)
    
    local_ips = []
    try:
        local_ips = socket.gethostbyname_ex(socket.gethostname())[2]
    except Exception:
        pass

    print(f"PICT Marketplace running at:")
    print(f"  - Local:   http://localhost:{port}/")
    for ip in local_ips:
        if not ip.startswith("127."):
            print(f"  - Network: http://{ip}:{port}/")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

def run_cli_scan(image_path: str):
    """CLI utility to scan a book or notes photo."""
    path = Path(image_path)
    if not path.exists():
        print(f"File not found: {image_path}")
        return
    mime, _ = mimetypes.guess_type(image_path)
    mime = mime or "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data_uri = f"data:{mime};base64,{b64}"
    print(f"Analyzing {image_path} with Sarvam AI Vision...")
    result = analyze_study_material_image(data_uri)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_connection()
    elif len(sys.argv) > 2 and sys.argv[1] == "--cli":
        run_cli_scan(sys.argv[2])
    else:
        port = PORT
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
        run_server(port)
