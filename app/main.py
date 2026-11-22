import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.config import STATIC_DIR, TEMPLATES_DIR, BACKUP_DIR
from app.database import (
    init_db, add_log, get_all_posts, get_recent_logs, 
    get_all_settings, set_setting, get_setting, save_post
)
from app.services.trend_radar import fetch_trending_topics
from app.services.gemini_ai import generate_viral_post, generate_reels_script, generate_comment_reply
from app.services.image_generator import generate_ai_image
from app.services.facebook_service import test_facebook_connection, publish_to_facebook, fetch_page_insights
from app.services.scheduler_service import start_scheduler, stop_scheduler, get_scheduler_status
from app.services.backup_service import create_full_system_zip, get_backup_summary
from app.pipeline import run_auto_pilot_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and check auto-pilot state
    init_db()
    from app.database import create_local_backup
    try:
        startup_backup = create_local_backup()
        add_log(f"Automatic startup backup created: {os.path.basename(startup_backup)}", "SUCCESS", "STARTUP_BACKUP")
    except Exception as e:
        print("Startup backup notice:", e)

    add_log("PiyushSocial AI Master Server started", "SUCCESS", "SYSTEM_STARTUP")
    
    # Auto-resume scheduler if it was enabled in settings
    if get_setting("auto_pilot_enabled", "false").lower() == "true":
        interval = float(get_setting("interval_hours", "1.0"))
        start_scheduler(hours=interval)
        
    yield
    # Shutdown
    add_log("PiyushSocial AI Server shutting down...", "INFO", "SYSTEM_SHUTDOWN")

app = FastAPI(
    title="PiyushSocial AI - Elite Facebook Page Manager",
    description="Autonomous AI Facebook Page Manager, Content Studio, and 24/7 Auto-Pilot Engine",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static and Templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Request Models
class GenerateRequest(BaseModel):
    topic: str
    pillar: Optional[str] = "Trending News & Analysis"
    persona: Optional[str] = "Inspiring Tech Creator"
    language: Optional[str] = "Bengali & English Mixed"

class PublishRequest(BaseModel):
    topic: str
    content: str
    hook: Optional[str] = ""
    hashtags: Optional[str] = ""
    local_image_path: Optional[str] = None
    image_url: Optional[str] = None
    pillar: Optional[str] = "General"

class SchedulerToggleRequest(BaseModel):
    enabled: bool
    interval_hours: Optional[float] = 1.0

class SettingsUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    facebook_page_id: Optional[str] = None
    facebook_page_access_token: Optional[str] = None
    brand_name: Optional[str] = None
    content_language: Optional[str] = None
    enable_watermark: Optional[bool] = None

class CommentReplyRequest(BaseModel):
    comment: str
    topic: str

class ReelsRequest(BaseModel):
    topic: str

# Web Route
@app.get("/", response_class=HTMLResponse)
async def home_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# API Routes
# Complete Multi-Page Registry with Permanent Never-Expiring Tokens (Expires at: 0)
PAGE_REGISTRY = {
    "296032910256028": {
        "id": "296032910256028",
        "name": "piyush#clips",
        "followers": 193,
        "category": "Photography and Videography",
        "token": "EAAQM1pkpef8BTBJaz0rhps7p1o4YGBPZCVGSFxKmQ0V01G1XkObr6J5KKrSwNFVBkRZAqPcS0l6DAVVHnM773pa4xPBX6ofzbpkjyktOEb7XnL3guZAMi7bPRq9L99sWLmXuJmWoRcOtKRY7thR9749nhM710XFMir2aD4Hg45fn31nhZAjVN8PjHmgW54EU470eKuL4"
    },
    "901244763082173": {
        "id": "901244763082173",
        "name": "American AI Hub",
        "followers": 0,
        "category": "Digital Creator",
        "token": "EAAQM1pkpef8BTI23sMEveJnAh9d9ifCcwWd3gMgvZApZAJLobGtZC3Fi5JAaoSL7fVBLMP1elVuo6zTzs8sZBOjAqmdL2G6eSjYab28ML7eZCjoUPKmbMftctjNQ2X26WZCaXpAdN3QdxShTk1h1AZA8DOwnITn6ZAGpZCZCSye5RdJtollpD1O2nQUkOF0rgGcOEoOsEK"
    },
    "167964807290916": {
        "id": "167964807290916",
        "name": "Earn Money",
        "followers": 1,
        "category": "Product/Service",
        "token": "EAAQM1pkpef8BTOUzyGzC6IhKoEROwBw9mpSOBZA4yWUtLcj8f7ZBqfqyEUSbahvn3z0U4ZAmK1ksnLnmYX9Pyj3QW2d63JAyNh65VKh0cikSA5zXwal1NZAjlDP0jcRHL0RuwFSWi12ZBFbzapSvyUGZBVAsWakOpBKk2uaPG9bckAMGV68yvHPYRAgf1BEVoXcG8ZD"
    }
}

@app.get("/api/pages")
async def get_available_pages():
    current_page_id = get_setting("facebook_page_id", "296032910256028")
    pages_list = [
        {"id": p["id"], "name": p["name"], "followers": p["followers"], "category": p["category"]}
        for p in PAGE_REGISTRY.values()
    ]
    return {
        "current_page_id": current_page_id,
        "pages": pages_list
    }

class PageSwitchRequest(BaseModel):
    page_id: str

@app.post("/api/pages/switch")
async def switch_page(req: PageSwitchRequest):
    selected = PAGE_REGISTRY.get(req.page_id)
    if not selected:
        raise HTTPException(status_code=404, detail="Page not found")
        
    # Update both page id and token in settings
    set_setting("facebook_page_id", selected["id"])
    set_setting("facebook_page_access_token", selected["token"])
    set_setting("brand_name", selected["name"])
    
    add_log(f"Active Facebook Page switched to: {selected['name']} (ID: {selected['id']})", "SUCCESS", "PAGE_SWITCH")
    
    return {
        "success": True,
        "page_id": selected["id"],
        "page_name": selected["name"],
        "followers": selected["followers"],
        "message": f"Switched to {selected['name']} successfully!"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "PiyushSocial AI", "version": "2.0.0"}

@app.get("/api/status")
async def get_system_status():
    scheduler_info = get_scheduler_status()
    fb_status = test_facebook_connection()
    insights = fetch_page_insights()
    all_posts = get_all_posts(limit=10)
    
    return {
        "scheduler": scheduler_info,
        "facebook": fb_status,
        "insights": insights,
        "total_posts_created": len(all_posts),
        "recent_posts": all_posts
    }

@app.get("/api/trends")
async def get_trends(region: str = "world"):
    topics = fetch_trending_topics(region=region, limit=12)
    return {"trends": topics}

@app.post("/api/generate-preview")
async def generate_preview(req: GenerateRequest):
    """Generates post copy + image for user review before publishing."""
    ai_content = generate_viral_post(
        topic=req.topic, 
        pillar=req.pillar, 
        persona=req.persona, 
        language=req.language
    )
    
    image_prompt = ai_content.get("image_prompt", req.topic)
    brand = get_setting("brand_name", "NovaSocial AI")
    img_data = generate_ai_image(prompt=image_prompt, brand_watermark=brand)
    
    return {
        "success": True,
        "topic": req.topic,
        "ai_content": ai_content,
        "image": img_data
    }

@app.post("/api/publish-now")
async def publish_now(req: PublishRequest):
    """Publishes a verified post with image directly to Facebook Page."""
    fb_res = publish_to_facebook(message=req.content, local_image_path=req.local_image_path)
    
    fb_post_id = fb_res.get("post_id", "demo_id")
    status = "published" if fb_res.get("success") else "failed"
    
    post_id = save_post(
        topic=req.topic,
        hook=req.hook,
        content=req.content,
        hashtags=req.hashtags,
        image_url=req.image_url,
        local_image_path=req.local_image_path,
        fb_post_id=fb_post_id,
        status=status,
        niche=req.pillar
    )
    
    return {
        "success": fb_res.get("success", False),
        "post_id": post_id,
        "fb_response": fb_res
    }

@app.post("/api/trigger-pipeline")
async def trigger_pipeline_immediate(background_tasks: BackgroundTasks, topic: Optional[str] = None):
    """Triggers the full autonomous pipeline immediately in the background."""
    background_tasks.add_task(run_auto_pilot_pipeline, topic=topic)
    return {"success": True, "message": "Autonomous auto-pilot pipeline dispatched in background!"}

@app.post("/api/scheduler/toggle")
async def toggle_scheduler(req: SchedulerToggleRequest):
    if req.enabled:
        start_scheduler(hours=req.interval_hours or 1.0)
    else:
        stop_scheduler()
    return get_scheduler_status()

@app.get("/api/posts")
async def get_posts():
    return {"posts": get_all_posts(limit=100)}

@app.get("/api/logs")
async def get_logs():
    return {"logs": get_recent_logs(limit=40)}

@app.post("/api/reels/generate")
async def generate_reels(req: ReelsRequest):
    script = generate_reels_script(topic=req.topic)
    return {"success": True, "script": script}

@app.post("/api/comments/reply")
async def comment_reply(req: CommentReplyRequest):
    reply_text = generate_comment_reply(comment=req.comment, post_topic=req.topic)
    return {"success": True, "reply": reply_text}

@app.get("/api/settings")
async def read_settings():
    return get_all_settings()

@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    if req.gemini_api_key is not None:
        set_setting("gemini_api_key", req.gemini_api_key)
    if req.facebook_page_id is not None:
        set_setting("facebook_page_id", req.facebook_page_id)
    if req.facebook_page_access_token is not None:
        set_setting("facebook_page_access_token", req.facebook_page_access_token)
    if req.brand_name is not None:
        set_setting("brand_name", req.brand_name)
    if req.content_language is not None:
        set_setting("content_language", req.content_language)
    if req.enable_watermark is not None:
        set_setting("enable_watermark", str(req.enable_watermark).lower())
        
    add_log("Settings updated via web dashboard", "INFO", "SETTINGS_UPDATE")
    return {"success": True, "settings": get_all_settings()}

@app.post("/api/backup/auto-sync")
async def trigger_auto_backup_on_open():
    """Triggered automatically whenever the user opens the app on their laptop."""
    from app.services.backup_service import create_full_system_zip
    from app.database import create_local_backup
    
    # Create database snapshot
    db_snapshot = create_local_backup()
    add_log(f"Auto-backup triggered upon opening app: {os.path.basename(db_snapshot)}", "SUCCESS", "AUTO_BACKUP_ON_OPEN")
    
    return {
        "success": True,
        "message": "Automatic Laptop Backup Completed!",
        "file": os.path.basename(db_snapshot),
        "backup_dir": str(BACKUP_DIR),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/api/audit/run")
async def run_profile_audit():
    """Fetches full page engagement/views and runs deep AI analysis with personalized recommendations."""
    from app.services.facebook_service import fetch_deep_page_metrics
    from app.services.gemini_ai import generate_deep_profile_audit
    
    metrics = fetch_deep_page_metrics()
    audit_report = generate_deep_profile_audit(metrics)
    
    add_log(f"Profile Audit complete. Health Score: {audit_report.get('health_score')}/100", "SUCCESS", "PROFILE_AUDIT")
    
    return {
        "success": True,
        "metrics": metrics,
        "audit": audit_report,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/backup/download")
async def download_backup():
    """Download full ZIP archive for offline laptop backup."""
    zip_path = create_full_system_zip()
    return FileResponse(
        path=zip_path,
        filename=os.path.basename(zip_path),
        media_type="application/zip"
    )

@app.get("/api/backup/status")
async def backup_status():
    return get_backup_summary()
