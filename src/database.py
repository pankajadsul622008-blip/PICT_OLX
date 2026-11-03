import sqlite3
from typing import List, Dict, Any
from .config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite schema for listings."""
    with get_connection() as conn:
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

def get_all_listings() -> List[Dict[str, Any]]:
    """Fetches all listings ordered by most recent."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM listings ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def create_listing(payload: Dict[str, Any]) -> int:
    """Inserts a new listing and returns its ID."""
    with get_connection() as conn:
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
        return cursor.lastrowid

