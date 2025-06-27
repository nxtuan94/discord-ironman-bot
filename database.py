import sqlite3
from datetime import datetime

DB_FILE = "checkin.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        # Bảng người dùng
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT
            )
        """)
        # Bảng check-in (mỗi lần check-in riêng biệt)
        c.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT
            )
        """)
        # Bảng ảnh gắn với từng lần check-in
        c.execute("""
            CREATE TABLE IF NOT EXISTS images (
                checkin_id INTEGER,
                image_url TEXT
            )
        """)
        # Bảng lưu cache xếp hạng từng tháng
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


def add_user(user_id, username):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username))
        conn.commit()


def get_all_users():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, username FROM users")
        return dict(c.fetchall())


def add_checkin(user_id, timestamp, image_urls=None):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO checkins (user_id, timestamp) VALUES (?, ?)",
                  (user_id, timestamp))
        checkin_id = c.lastrowid
        if image_urls:
            for url in image_urls:
                c.execute(
                    "INSERT INTO images (checkin_id, image_url) VALUES (?, ?)",
                    (checkin_id, url))
        conn.commit()
        return checkin_id


def get_checkin_images_by_date(date_prefix):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT checkins.user_id, images.image_url
            FROM checkins
            JOIN images ON checkins.id = images.checkin_id
            WHERE checkins.timestamp LIKE ?
        """, (f"{date_prefix}%", ))
        result = {}
        for uid, url in c.fetchall():
            result.setdefault(uid, []).append(url)
        return result


def get_user_checkin_dates(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT timestamp FROM checkins WHERE user_id = ?",
                  (user_id, ))
        return sorted([row[0][:10] for row in c.fetchall()])


def save_rank(month, user_id, total_days, best_streak, current_streak):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
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
        c.execute(
            "SELECT user_id, total_days, best_streak, current_streak FROM ranks WHERE month = ?",
            (month, ))
        return {
            row[0]: {
                "total": row[1],
                "best_streak": row[2],
                "current_streak": row[3]
            }
            for row in c.fetchall()
        }
