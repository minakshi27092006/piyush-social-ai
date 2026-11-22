import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
BACKUP_DIR = BASE_DIR / "backups"
IMAGES_DIR = STATIC_DIR / "images"

# Ensure crucial directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

class AppSettings(BaseModel):
    app_name: str = "PiyushSocial AI - Elite Facebook Content Engine"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    facebook_page_id: str = os.getenv("FACEBOOK_PAGE_ID", "")
    facebook_page_access_token: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    
    # Auto-pilot settings
    auto_pilot_enabled: bool = False
    interval_hours: float = 1.0  # Default every 1 hour
    content_language: str = "Bengali & English Mixed (Smart Banglish/Bengali)"
    default_niche: str = "Technology, AI, Viral Trends & Motivation"
    brand_name: str = "PiyushSocial AI"
    enable_watermark: bool = True

settings = AppSettings()
