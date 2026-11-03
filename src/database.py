import sqlite3
from typing import List, Dict, Any, Optional
from .config import DATABASE_URL, DB_PATH

# Check if PostgreSQL (Supabase) is configured
USE_POSTGRES = bool(DATABASE_URL and DATABASE_URL.startswith("postgres"))

if USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        USE_POSTGRES = False

def get_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema (Supabase PostgreSQL or SQLite)."""
    if USE_POSTGRES:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id BIGSERIAL PRIMARY KEY,
                            email TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL,
                            name TEXT NOT NULL,
                            phone TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS sessions (
                            token TEXT PRIMARY KEY,
                            user_id BIGINT NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS listings (
                            id BIGSERIAL PRIMARY KEY,
                            user_id BIGINT,
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
                            is_sold BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );

                        ALTER TABLE listings ADD COLUMN IF NOT EXISTS user_id BIGINT;
                        ALTER TABLE listings ADD COLUMN IF NOT EXISTS is_sold BOOLEAN DEFAULT FALSE;
                    """)
                    conn.commit()
            print("Connected to Supabase PostgreSQL: schema verified.")
            return
        except Exception as e:
            print(f"Warning: Failed to connect to Supabase PostgreSQL ({e}). Falling back to local SQLite.")

    # SQLite Fallback
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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
                is_sold BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            conn.execute("ALTER TABLE listings ADD COLUMN user_id INTEGER;")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE listings ADD COLUMN is_sold BOOLEAN DEFAULT 0;")
        except Exception:
            pass
        conn.commit()
    print("Using local SQLite database: listings.db")

def get_all_listings() -> List[Dict[str, Any]]:
    """Fetches all listings ordered by most recent."""
    if USE_POSTGRES:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM listings ORDER BY id DESC")
                    rows = cur.fetchall()
                    result = []
                    for r in rows:
                        d = dict(r)
                        if d.get("created_at"):
                            d["created_at"] = str(d["created_at"])
                        d["is_sold"] = bool(d.get("is_sold", False))
                        result.append(d)
                    return result
        except Exception as e:
            print(f"Error fetching from Supabase: {e}, attempting SQLite fallback...")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM listings ORDER BY id DESC")
        result = []
        for row in cursor.fetchall():
            d = dict(row)
            d["is_sold"] = bool(d.get("is_sold", False))
            result.append(d)
        return result

def create_listing(payload: Dict[str, Any], user_id: Optional[int] = None) -> int:
    """Inserts a new listing and returns its ID."""
    uid = user_id or payload.get("user_id")
    values = (
        uid,
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
    )

    if USE_POSTGRES:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO listings (
                            user_id, title, subject, department, target_year, semester,
                            material_type, condition, price_inr, original_mrp,
                            description, seller_name, seller_contact, image_data_uri
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """, values)
                    conn.commit()
                    return cur.fetchone()[0]
        except Exception as e:
            print(f"Error inserting into Supabase: {e}, attempting SQLite fallback...")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO listings (
                user_id, title, subject, department, target_year, semester,
                material_type, condition, price_inr, original_mrp,
                description, seller_name, seller_contact, image_data_uri
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, values)
        conn.commit()
        return cursor.lastrowid

def mark_listing_sold(listing_id: int, user_id: int) -> bool:
    """Marks a listing as sold if owned by user_id."""
    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE listings SET is_sold = TRUE 
                    WHERE id = %s AND (user_id = %s OR user_id IS NULL)
                """, (listing_id, user_id))
                conn.commit()
                return cur.rowcount > 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE listings SET is_sold = 1 
            WHERE id = ? AND (user_id = ? OR user_id IS NULL)
        """, (listing_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_listing(listing_id: int, user_id: int) -> bool:
    """Deletes a listing if owned by user_id."""
    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM listings 
                    WHERE id = %s AND (user_id = %s OR user_id IS NULL)
                """, (listing_id, user_id))
                conn.commit()
                return cur.rowcount > 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM listings 
            WHERE id = ? AND (user_id = ? OR user_id IS NULL)
        """, (listing_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
