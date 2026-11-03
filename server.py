import os
import sys
import json
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from sarvamai import SarvamAI

# Load .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

DB_PATH = Path(__file__).parent / "listings.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT,
                department TEXT,
                target_year TEXT,
                semester TEXT,
                material_type TEXT,
                condition TEXT,
                price_inr INTEGER,
                original_mrp INTEGER,
                description TEXT,
                seller_name TEXT,
                seller_contact TEXT,
                image_data_uri TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

def get_sarvam_client() -> SarvamAI:
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is not configured in .env")
    return SarvamAI(api_subscription_key=api_key)

def analyze_study_material_image(data_uri: str) -> dict:
    client = get_sarvam_client()
    system_prompt = (
        "You are an AI assistant for a college study material marketplace at PICT "
        "(Pune Institute of Computer Technology, affiliated with SPPU - Pune University). "
        "A senior student is listing used study material (textbook, handwritten notes, "
        "PYQ question booklet, lab manual, engineering drafter/kit).\n"
        "Analyze the provided image and extract accurate details.\n"
        "Return ONLY a valid JSON object with the following keys:\n"
        "{\n"
        '  "title": "Clean, descriptive title for the listing",\n'
        '  "subject": "Subject name according to SPPU curriculum (e.g. Data Structures, OS, CN, TOC, EM-3)",\n'
        '  "department": "One of: Computer Engineering, Information Technology, E&TC, AIDS, First Year (FE), General",\n'
        '  "target_year": "One of: FE, SE, TE, BE",\n'
        '  "semester": "Semester 1 through 8",\n'
        '  "material_type": "One of: Textbook, Handwritten Notes, Question Bank / PYQ, Lab Manual, Tool / Instrument",\n'
        '  "publisher_or_author": "e.g. Nirali Prakashan, TechKnowledge, Pearson, McGraw-Hill, or Senior Handwritten",\n'
        '  "detected_condition": "One of: Like New, Good, Annotated / Highlighted, Fair / Worn",\n'
        '  "suggested_price_inr": integer resale price in INR (40-60% off typical MRP),\n'
        '  "estimated_mrp_inr": integer estimated original MRP in INR,\n'
        '  "description": "A helpful 2-sentence description for juniors highlighting utility and condition",\n'
        '  "search_tags": ["list", "of", "relevant", "keywords"]\n'
        "}\n"
        "Do not include any markdown backticks or extra text outside JSON."
    )
    
    response = client.chat.completions_v2(
        model="gemma4",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ],
        temperature=0.2
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return json.loads(content)

class MarketplaceHandler(BaseHTTPRequestHandler):
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
        if self.path == "/" or self.path == "/index.html":
            html_file = Path(__file__).parent / "index.html"
            if html_file.exists():
                content = html_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "index.html not found")
        elif self.path == "/api/listings":
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM listings ORDER BY id DESC")
                rows = [dict(r) for r in cursor.fetchall()]
            self._send_json({"listings": rows})
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

        elif self.path == "/api/listings":
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO listings (
                            title, subject, department, target_year, semester,
                            material_type, condition, price_inr, original_mrp,
                            description, seller_name, seller_contact, image_data_uri
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        payload.get("title", "Untitled Listing"),
                        payload.get("subject", ""),
                        payload.get("department", "General"),
                        payload.get("target_year", "FE"),
                        payload.get("semester", ""),
                        payload.get("material_type", "Textbook"),
                        payload.get("condition", "Good"),
                        int(payload.get("price_inr") or 0),
                        int(payload.get("original_mrp") or 0),
                        payload.get("description", ""),
                        payload.get("seller_name", "PICT Senior"),
                        payload.get("seller_contact", ""),
                        payload.get("image_data_uri", "")
                    ))
                    conn.commit()
                    new_id = cursor.lastrowid
                self._send_json({"success": True, "id": new_id})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Not Found")

def run(port=8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, MarketplaceHandler)
    print(f"PICT Marketplace server running at http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
