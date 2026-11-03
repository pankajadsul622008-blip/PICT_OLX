import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
TEMPLATES_DIR = SRC_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
ENV_FILE = BASE_DIR / ".env"

# Load .env file if present
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

# Server Configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

# Database Configuration
DATABASE_NAME = os.environ.get("DATABASE_NAME", "listings.db")
DB_PATH = BASE_DIR / DATABASE_NAME

# Sarvam AI Credentials & Models
SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")
SARVAM_VISION_MODEL = os.environ.get("SARVAM_VISION_MODEL", "gemma4")
SARVAM_CHAT_MODEL = os.environ.get("SARVAM_CHAT_MODEL", "sarvam-105b-conversations")

# Campus & WhatsApp Regional Settings
COLLEGE_NAME = os.environ.get("COLLEGE_NAME", "PICT")
COLLEGE_FULL_NAME = os.environ.get("COLLEGE_FULL_NAME", "Pune Institute of Computer Technology")
UNIVERSITY_NAME = os.environ.get("UNIVERSITY_NAME", "SPPU")
WHATSAPP_DEFAULT_COUNTRY_CODE = os.environ.get("WHATSAPP_DEFAULT_COUNTRY_CODE", "91")
DEFAULT_CURRENCY = os.environ.get("DEFAULT_CURRENCY", "INR")
