import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "checkin.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkin_id INTEGER,
                image_url TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS ranks (
                month TEXT,
                user_id TEXT,
                total_days INTEGER,
                best_streak INTEGER,
                current_streak INTEGER,
                PRIMARY KEY (month, user_id)
            )
        """)

        conn.commit()

def get_all_users():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, username FROM users")
        return {row[0]: row[1] for row in c.fetchall()}

def get_user_checkin_dates(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT timestamp FROM checkins WHERE user_id = ?", (user_id,))
        return sorted([row[0][:10] for row in c.fetchall()])

def get_checkin_images_by_date(date_prefix):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT checkins.user_id, images.image_url
            FROM checkins
            JOIN images ON checkins.id = images.checkin_id
            WHERE checkins.timestamp LIKE ?
        """, (f"{date_prefix}%",))
        result = {}
        for uid, url in c.fetchall():
            result.setdefault(uid, []).append(url)
        return result

def add_user(user_id, username):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

def add_checkin(user_id, timestamp, image_urls):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO checkins (user_id, timestamp) VALUES (?, ?)", (user_id, timestamp))
        checkin_id = c.lastrowid
        for url in image_urls:
            c.execute("INSERT INTO images (checkin_id, image_url) VALUES (?, ?)", (checkin_id, url))
        conn.commit()

def save_rank(month, user_id, total_days, best_streak, current_streak):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO ranks (month, user_id, total_days, best_streak, current_streak)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(month, user_id) DO UPDATE SET
                total_days=excluded.total_days,
                best_streak=excluded.best_streak,
                current_streak=excluded.current_streak
        """, (month, user_id, total_days, best_streak, current_streak))
        conn.commit()

def get_ranks_for_month(month):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, total_days, best_streak, current_streak FROM ranks WHERE month = ?", (month,))
        return {
            row[0]: {
                "total": row[1],
                "best_streak": row[2],
                "current_streak": row[3]
            }
            for row in c.fetchall()
        }

def delete_rank_cache_for_date(date_str):
    month_prefix = date_str[:7]  # YYYY-MM
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ranks WHERE month = ?", (month_prefix,))
        conn.commit()