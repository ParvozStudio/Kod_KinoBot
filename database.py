import sqlite3
from datetime import datetime
from contextlib import contextmanager

from config import DB_PATH, OWNER_ID


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                added_by INTEGER,
                added_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE COLLATE NOCASE,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                file_id TEXT NOT NULL,
                added_by INTEGER,
                added_at TEXT,
                views INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS view_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_id INTEGER,
                viewed_at TEXT
            )
        """)
        if OWNER_ID:
            cur.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)",
                (OWNER_ID, OWNER_ID, datetime.utcnow().isoformat()),
            )


# ---------------- USERS ----------------

def add_user(user_id: int, username: str, full_name: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, joined_at) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, datetime.utcnow().isoformat()),
        )


def get_users_count() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]


def get_all_user_ids():
    with get_conn() as conn:
        rows = conn.execute("SELECT user_id FROM users").fetchall()
        return [r["user_id"] for r in rows]


# ---------------- ADMINS ----------------

def is_admin(user_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
        return row is not None


def add_admin(user_id: int, added_by: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)",
            (user_id, added_by, datetime.utcnow().isoformat()),
        )


def remove_admin(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))


def get_admins():
    with get_conn() as conn:
        return [r["user_id"] for r in conn.execute("SELECT user_id FROM admins").fetchall()]


# ---------------- VIDEOS (KOD ORQALI) ----------------

class DuplicateCodeError(Exception):
    pass


def add_video(code: str, category: str, title: str, description: str, file_id: str, added_by: int) -> int:
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO videos (code, category, title, description, file_id, added_by, added_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (code, category, title, description, file_id, added_by, datetime.utcnow().isoformat()),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise DuplicateCodeError(f"'{code}' kodi allaqachon band")


def get_video_by_code(code: str):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM videos WHERE code = ?", (code.strip(),)).fetchone()


def delete_video_by_code(code: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM videos WHERE code = ?", (code.strip(),))
        return cur.rowcount > 0


def increment_view(video_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE videos SET views = views + 1 WHERE id=?", (video_id,))
        conn.execute(
            "INSERT INTO view_log (user_id, video_id, viewed_at) VALUES (?, ?, ?)",
            (user_id, video_id, datetime.utcnow().isoformat()),
        )


def get_stats():
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        total_videos = conn.execute("SELECT COUNT(*) c FROM videos").fetchone()["c"]
        total_views = conn.execute("SELECT COALESCE(SUM(views),0) c FROM videos").fetchone()["c"]
        by_category = conn.execute(
            "SELECT category, COUNT(*) c FROM videos GROUP BY category"
        ).fetchall()
        top_videos = conn.execute(
            "SELECT title, code, views FROM videos ORDER BY views DESC LIMIT 5"
        ).fetchall()
        return {
            "total_users": total_users,
            "total_videos": total_videos,
            "total_views": total_views,
            "by_category": {r["category"]: r["c"] for r in by_category},
            "top_videos": [(r["title"], r["code"], r["views"]) for r in top_videos],
        }
