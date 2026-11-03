import os
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Any

from ..database import USE_POSTGRES, DB_PATH
from ..config import DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
else:
    import sqlite3

def hash_password(password: str) -> str:
    """Hashes password using PBKDF2-HMAC-SHA256 with a secure random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}:{key.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a password against the stored salt:hash string."""
    try:
        salt, key_hex = stored_hash.split(":")
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False

def ensure_admin_user():
    """Seeds or promotes the configured admin user."""
    admin_email = ADMIN_EMAIL.strip().lower()
    admin_hash = hash_password(ADMIN_PASSWORD)

    if USE_POSTGRES:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
                    existing = cur.fetchone()
                    if existing:
                        cur.execute("""
                            UPDATE users 
                            SET is_admin = TRUE, password_hash = %s, name = 'Campus Administrator' 
                            WHERE email = %s
                        """, (admin_hash, admin_email))
                    else:
                        cur.execute("""
                            INSERT INTO users (email, password_hash, name, phone, is_admin)
                            VALUES (%s, %s, 'Campus Administrator', '0000000000', TRUE)
                        """, (admin_email, admin_hash))
                    conn.commit()
            print(f"Admin account verified: {admin_email}")
            return
        except Exception as e:
            print(f"Warning: Could not seed admin in Supabase ({e})")

    # SQLite
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
            if cur.fetchone():
                cur.execute("""
                    UPDATE users 
                    SET is_admin = 1, password_hash = ?, name = 'Campus Administrator' 
                    WHERE email = ?
                """, (admin_hash, admin_email))
            else:
                cur.execute("""
                    INSERT INTO users (email, password_hash, name, phone, is_admin)
                    VALUES (?, ?, 'Campus Administrator', '0000000000', 1)
                """, (admin_email, admin_hash))
            conn.commit()
        print(f"Admin account verified (SQLite): {admin_email}")
    except Exception as e:
        print(f"Warning: Could not seed admin in SQLite ({e})")

def register_user(email: str, password: str, name: str, phone: str = "") -> Dict[str, Any]:
    """Registers a new user and returns user info + session token."""
    email = email.strip().lower()
    if not email or not password or not name:
        raise ValueError("Email, password, and name are required.")

    is_admin = (email == ADMIN_EMAIL.strip().lower())
    pwd_hash = hash_password(password)

    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check duplicate
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    raise ValueError("An account with this email already exists.")

                cur.execute("""
                    INSERT INTO users (email, password_hash, name, phone, is_admin)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, email, name, phone, is_admin;
                """, (email, pwd_hash, name, phone, is_admin))
                user = dict(cur.fetchone())
                user["is_admin"] = bool(user.get("is_admin", False))

                token = secrets.token_hex(32)
                cur.execute("INSERT INTO sessions (token, user_id) VALUES (%s, %s)", (token, user["id"]))
                conn.commit()
                user["token"] = token
                return user

    # SQLite fallback
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            raise ValueError("An account with this email already exists.")

        cur.execute("""
            INSERT INTO users (email, password_hash, name, phone, is_admin)
            VALUES (?, ?, ?, ?, ?)
        """, (email, pwd_hash, name, phone, 1 if is_admin else 0))
        user_id = cur.lastrowid
        token = secrets.token_hex(32)
        cur.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        conn.commit()
        return {"id": user_id, "email": email, "name": name, "phone": phone, "is_admin": is_admin, "token": token}

def login_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticates user and returns user info + new session token."""
    email = email.strip().lower()

    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                if not user or not verify_password(password, user["password_hash"]):
                    raise ValueError("Invalid email or password.")

                user = dict(user)
                user.pop("password_hash", None)
                if user.get("created_at"):
                    user["created_at"] = str(user["created_at"])
                user["is_admin"] = bool(user.get("is_admin", False))
                token = secrets.token_hex(32)
                cur.execute("INSERT INTO sessions (token, user_id) VALUES (%s, %s)", (token, user["id"]))
                conn.commit()
                user["token"] = token
                return user

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            raise ValueError("Invalid email or password.")

        user = dict(row)
        user.pop("password_hash", None)
        user["is_admin"] = bool(user.get("is_admin", 0))
        token = secrets.token_hex(32)
        cur.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
        conn.commit()
        user["token"] = token
        return user

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Resolves session token to user dict."""
    if not token:
        return None

    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT u.id, u.email, u.name, u.phone, u.is_admin, u.created_at
                    FROM sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.token = %s;
                """, (token,))
                row = cur.fetchone()
                if row:
                    res = dict(row)
                    if res.get("created_at"):
                        res["created_at"] = str(res["created_at"])
                    res["is_admin"] = bool(res.get("is_admin", False))
                    return res
                return None

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.email, u.name, u.phone, u.is_admin, u.created_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?;
        """, (token,))
        row = cur.fetchone()
        if row:
            res = dict(row)
            res["is_admin"] = bool(res.get("is_admin", 0))
            return res
        return None

def logout_user(token: str) -> bool:
    """Removes the session token."""
    if not token:
        return False
    if USE_POSTGRES:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
                conn.commit()
                return True
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        return True
