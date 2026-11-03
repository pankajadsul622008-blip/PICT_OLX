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
                            is_admin BOOLEAN DEFAULT FALSE,
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

                        ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
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
                is_admin BOOLEAN DEFAULT 0,
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
            conn.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;")
        except Exception:
            pass
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

def update_listing(listing_id: int, payload: Dict[str, Any], user_id: int, is_admin: bool = False) -> bool:
    """Updates listing content if user is owner or admin."""
    fields = [
        ("title", payload.get("title")),
        ("subject", payload.get("subject")),
        ("department", payload.get("department")),
        ("target_year", payload.get("target_year")),
        ("semester", payload.get("semester")),
        ("material_type", payload.get("material_type")),
        ("condition", payload.get("condition")),
        ("price_inr", int(payload.get("price_inr")) if payload.get("price_inr") is not None else None),
        ("original_mrp", int(payload.get("original_mrp")) if payload.get("original_mrp") is not None else None),
        ("description", payload.get("description")),
    ]
    if payload.get("image_data_uri"):
        fields.append(("image_data_uri", payload.get("image_data_uri")))

    update_clauses = [f"{k} = %s" for k, v in fields if v is not None]
    update_values = [v for k, v in fields if v is not None]
    if not update_clauses:
        return True

    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                if is_admin:
                    sql = f"UPDATE listings SET {', '.join(update_clauses)} WHERE id = %s"
                    cur.execute(sql, (*update_values, listing_id))
                else:
                    sql = f"UPDATE listings SET {', '.join(update_clauses)} WHERE id = %s AND (user_id = %s OR user_id IS NULL)"
                    cur.execute(sql, (*update_values, listing_id, user_id))
                conn.commit()
                return cur.rowcount > 0

    # SQLite
    sqlite_clauses = [f"{k} = ?" for k, v in fields if v is not None]
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if is_admin:
            sql = f"UPDATE listings SET {', '.join(sqlite_clauses)} WHERE id = ?"
            cursor.execute(sql, (*update_values, listing_id))
        else:
            sql = f"UPDATE listings SET {', '.join(sqlite_clauses)} WHERE id = ? AND (user_id = ? OR user_id IS NULL)"
            cursor.execute(sql, (*update_values, listing_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def mark_listing_sold(listing_id: int, user_id: int, is_admin: bool = False, sold_status: bool = True) -> bool:
    """Marks a listing as sold or available if owned by user_id or admin."""
    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                if is_admin:
                    cur.execute("UPDATE listings SET is_sold = %s WHERE id = %s", (sold_status, listing_id))
                else:
                    cur.execute("UPDATE listings SET is_sold = %s WHERE id = %s AND (user_id = %s OR user_id IS NULL)", (sold_status, listing_id, user_id))
                conn.commit()
                return cur.rowcount > 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if is_admin:
            cursor.execute("UPDATE listings SET is_sold = ? WHERE id = ?", (1 if sold_status else 0, listing_id))
        else:
            cursor.execute("UPDATE listings SET is_sold = ? WHERE id = ? AND (user_id = ? OR user_id IS NULL)", (1 if sold_status else 0, listing_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_listing(listing_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Deletes a listing if owned by user_id or admin."""
    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                if is_admin:
                    cur.execute("DELETE FROM listings WHERE id = %s", (listing_id,))
                else:
                    cur.execute("DELETE FROM listings WHERE id = %s AND (user_id = %s OR user_id IS NULL)", (listing_id, user_id))
                conn.commit()
                return cur.rowcount > 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if is_admin:
            cursor.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
        else:
            cursor.execute("DELETE FROM listings WHERE id = ? AND (user_id = ? OR user_id IS NULL)", (listing_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
