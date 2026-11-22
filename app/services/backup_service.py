import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from app.config import BASE_DIR, BACKUP_DIR, IMAGES_DIR
from app.database import DB_PATH, add_log, create_local_backup, export_posts_json

def create_full_system_zip() -> str:
    """
    Creates a full ZIP backup archive containing:
    - SQLite database snapshot
    - All generated post images
    - JSON export of all posts
    - System logs
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Laptop_Master_Backup_{timestamp}.zip"
    zip_filepath = BACKUP_DIR / zip_filename
    
    # 1. Take fresh snapshot of SQLite DB
    db_backup = create_local_backup()
    json_export = export_posts_json()
    
    # 2. Package into ZIP
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add SQLite database
        if os.path.exists(DB_PATH):
            zipf.write(DB_PATH, arcname="facebook_bot.db")
        if os.path.exists(json_export):
            zipf.write(json_export, arcname="posts_export.json")
            
        # Add all generated images
        if os.path.exists(IMAGES_DIR):
            for root, _, files in os.walk(IMAGES_DIR):
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, IMAGES_DIR)
                    zipf.write(full_p, arcname=f"images/{rel_p}")
                    
    add_log(f"Complete offline backup created for Laptop: {zip_filename}", "SUCCESS", "BACKUP_SYSTEM")
    return str(zip_filepath)

def get_backup_summary() -> Dict[str, Any]:
    """Returns detailed statistics about offline backups on the laptop."""
    backups = []
    total_size = 0
    if os.path.exists(BACKUP_DIR):
        for f in os.listdir(BACKUP_DIR):
            p = BACKUP_DIR / f
            if p.is_file() and not f.startswith("."):
                size = p.stat().st_size
                total_size += size
                backups.append({
                    "filename": f,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
                
    backups.sort(key=lambda x: x["created"], reverse=True)
    return {
        "backup_dir": str(BACKUP_DIR),
        "total_backups": len(backups),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "latest_backups": backups[:5]
    }
