import sqlite3
import random
import string

DB_NAME = "url_shortener.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def create_short_url(user_id, long_url):
    conn = get_connection()
    cursor = conn.cursor()

    short_code = generate_short_code()

    while cursor.execute(
        "SELECT id FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone() is not None:
        short_code = generate_short_code()

    cursor.execute(
        "INSERT INTO urls (user_id, short_code, long_url) VALUES (?, ?, ?)",
        (user_id, short_code, long_url)
    )

    conn.commit()
    conn.close()

    return short_code


def get_long_url(short_code):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        "SELECT long_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    conn.close()

    if row:
        return row["long_url"]
    return None


def increment_clicks(short_code):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
        (short_code,)
    )

    conn.commit()
    conn.close()


def get_url_stats(short_code):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        "SELECT user_id, short_code, long_url, clicks, created_at FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    conn.close()
    return row


def get_user_urls(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        "SELECT short_code, long_url, clicks, created_at FROM urls WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

    conn.close()
    return rows