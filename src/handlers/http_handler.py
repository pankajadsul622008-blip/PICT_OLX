import json
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler

from ..config import (
    TEMPLATES_DIR,
    STATIC_DIR,
    COLLEGE_NAME,
    COLLEGE_FULL_NAME,
    UNIVERSITY_NAME,
    WHATSAPP_DEFAULT_COUNTRY_CODE,
    DEFAULT_CURRENCY,
)
from ..database import get_all_listings, create_listing, update_listing, mark_listing_sold, delete_listing
from ..services.sarvam_service import analyze_study_material_image
from ..services.cloudinary_service import upload_image
from ..services.auth_service import register_user, login_user, get_user_from_token, logout_user

class MarketplaceHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests for Campus Marketplace."""

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _get_auth_user(self):
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            return get_user_from_token(token)
        return None

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
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

        # API: Health Check for UptimeRobot (Eliminates Render cold start)
        elif self.path in ("/api/health", "/health"):
            import datetime
            self._send_json({
                "status": "healthy",
                "uptime": "active",
                "service": f"{COLLEGE_NAME} Campus Marketplace",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

        # API: Public config for frontend
        elif self.path == "/api/config":
            self._send_json({
                "college_name": COLLEGE_NAME,
                "college_full_name": COLLEGE_FULL_NAME,
                "university_name": UNIVERSITY_NAME,
                "country_code": WHATSAPP_DEFAULT_COUNTRY_CODE,
                "currency": DEFAULT_CURRENCY,
            })

        # API: Auth user status
        elif self.path == "/api/auth/me":
            user = self._get_auth_user()
            if user:
                self._send_json({"authenticated": True, "user": user})
            else:
                self._send_json({"authenticated": False, "user": None})

        # API: Get all listings
        elif self.path == "/api/listings":
            try:
                listings = get_all_listings()
                self._send_json({"listings": listings})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        # Favicon direct route
        elif self.path == "/favicon.ico":
            fav = STATIC_DIR / "favicon.png"
            if fav.exists():
                content = fav.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404)

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
        payload = {}
        if length > 0:
            try:
                payload = json.loads(post_data.decode("utf-8"))
            except Exception:
                self._send_json({"error": "Invalid JSON"}, status=400)
                return

        # API: User Registration
        if self.path == "/api/auth/register":
            email = payload.get("email")
            password = payload.get("password")
            name = payload.get("name")
            phone = payload.get("phone", "")
            try:
                user = register_user(email, password, name, phone)
                self._send_json({"success": True, "user": user, "token": user["token"]})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)

        # API: User Login
        elif self.path == "/api/auth/login":
            email = payload.get("email")
            password = payload.get("password")
            try:
                user = login_user(email, password)
                self._send_json({"success": True, "user": user, "token": user["token"]})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)

        # API: User Logout
        elif self.path == "/api/auth/logout":
            auth_header = self.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                logout_user(auth_header[7:].strip())
            self._send_json({"success": True})

        # API: AI Vision analysis of study material
        elif self.path == "/api/analyze":
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
                user = self._get_auth_user()
                user_id = user["id"] if user else None

                # Upload image to Cloudinary CDN
                raw_image = payload.get("image_data_uri", "")
                if raw_image:
                    payload["image_data_uri"] = upload_image(raw_image)

                new_id = create_listing(payload, user_id=user_id)
                self._send_json({"success": True, "id": new_id})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)

        # API: Edit listing content (Owner or Admin)
        elif self.path.startswith("/api/listings/") and self.path.endswith("/edit"):
            parts = self.path.strip("/").split("/")
            if len(parts) == 4 and parts[2].isdigit():
                listing_id = int(parts[2])
                user = self._get_auth_user()
                if not user:
                    self._send_json({"error": "Authentication required"}, status=401)
                    return
                is_admin = bool(user.get("is_admin", False))
                # If new photo uploaded, send to Cloudinary
                raw_image = payload.get("image_data_uri", "")
                if raw_image and raw_image.startswith("data:image"):
                    payload["image_data_uri"] = upload_image(raw_image)

                ok = update_listing(listing_id, payload, user_id=user["id"], is_admin=is_admin)
                if ok:
                    self._send_json({"success": True, "message": "Listing updated"})
                else:
                    self._send_json({"error": "Listing not found or unauthorized"}, status=403)
            else:
                self.send_error(400, "Invalid path")

        # API: Mark listing as sold or available
        elif self.path.startswith("/api/listings/") and self.path.endswith("/sold"):
            parts = self.path.strip("/").split("/")
            if len(parts) == 4 and parts[2].isdigit():
                listing_id = int(parts[2])
                user = self._get_auth_user()
                if not user:
                    self._send_json({"error": "Authentication required"}, status=401)
                    return
                is_admin = bool(user.get("is_admin", False))
                sold_val = payload.get("is_sold", True) if isinstance(payload, dict) and "is_sold" in payload else True
                ok = mark_listing_sold(listing_id, user["id"], is_admin=is_admin, sold_status=sold_val)
                if ok:
                    self._send_json({"success": True, "message": "Listing status updated"})
                else:
                    self._send_json({"error": "Listing not found or unauthorized"}, status=403)
            else:
                self.send_error(400, "Invalid path")

        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self):
        # API: Delete listing (Owner or Admin)
        if self.path.startswith("/api/listings/"):
            parts = self.path.strip("/").split("/")
            if len(parts) == 3 and parts[2].isdigit():
                listing_id = int(parts[2])
                user = self._get_auth_user()
                if not user:
                    self._send_json({"error": "Authentication required"}, status=401)
                    return
                is_admin = bool(user.get("is_admin", False))
                ok = delete_listing(listing_id, user["id"], is_admin=is_admin)
                if ok:
                    self._send_json({"success": True, "message": "Listing deleted"})
                else:
                    self._send_json({"error": "Listing not found or unauthorized"}, status=403)
            else:
                self.send_error(400, "Invalid path")
        else:
            self.send_error(404, "Not Found")
