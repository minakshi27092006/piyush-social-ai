import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import BASE_DIR, BACKUP_DIR

DB_PATH = BASE_DIR / "facebook_bot.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Posts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        hook TEXT,
        content TEXT NOT NULL,
        hashtags TEXT,
        image_url TEXT,
        local_image_path TEXT,
        fb_post_id TEXT,
        status TEXT DEFAULT 'draft', -- draft, scheduled, published, failed
        scheduled_for TEXT,
        published_at TEXT,
        likes_count INTEGER DEFAULT 0,
        comments_count INTEGER DEFAULT 0,
        shares_count INTEGER DEFAULT 0,
        reach_count INTEGER DEFAULT 0,
        niche TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # App Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # Activity Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT DEFAULT 'INFO',
        message TEXT NOT NULL,
        event_type TEXT
    )
    """)
    
    # Reels / Shorts Script Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reels_scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        hook TEXT NOT NULL,
        script_body TEXT NOT NULL,
        audio_trend_cue TEXT,
        visual_directions TEXT,
        cta TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Auto-initialize database schema on import
init_db()

# Helper Functions
def add_log(message: str, level: str = "INFO", event_type: str = "GENERAL"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (timestamp, level, message, event_type) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message, event_type)
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_posts(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_post(topic: str, content: str, hook: str = "", hashtags: str = "", 
              image_url: str = "", local_image_path: str = "", 
              fb_post_id: str = "", status: str = "published", 
              niche: str = "General") -> int:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO posts (topic, hook, content, hashtags, image_url, local_image_path, fb_post_id, status, published_at, niche, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (topic, hook, content, hashtags, image_url, local_image_path, fb_post_id, status, now if status == 'published' else None, niche, now))
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    add_log(f"New post recorded [ID: {post_id}] - Topic: {topic[:40]}...", "SUCCESS", "POST_RECORDED")
    return post_id

def get_setting(key: str, default: str = "") -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_all_settings() -> Dict[str, str]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}

# Backup & Export
def create_local_backup() -> str:
    """Create a local snapshot backup of the database in the backups folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"facebook_bot_backup_{timestamp}.sqlite"
    shutil.copy2(DB_PATH, backup_file)
    add_log(f"Offline database backup created: {backup_file.name}", "INFO", "BACKUP")
    return str(backup_file)

def export_posts_json() -> str:
    posts = get_all_posts(limit=1000)
    json_path = BACKUP_DIR / f"posts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    return str(json_path)
