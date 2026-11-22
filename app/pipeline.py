import time
from datetime import datetime
from typing import Dict, Any, Optional
from app.database import add_log, save_post, get_setting, create_local_backup
from app.services.trend_radar import get_single_hottest_topic
from app.services.gemini_ai import generate_viral_post
from app.services.image_generator import generate_ai_image
from app.services.facebook_service import publish_to_facebook

def run_auto_pilot_pipeline(topic: Optional[str] = None, 
                            pillar: str = "Trending News & Analysis",
                            persona: str = "Inspiring Tech Creator") -> Dict[str, Any]:
    """
    Autonomous Pipeline Execution:
    1. Trend Discovery: Fetches top hot trend if no custom topic is passed.
    2. Viral Copywriting: Generates hook, body, CTA, and hashtags via Gemini AI.
    3. Visual Synthesis: Synthesizes high-def graphic via Pollinations + Watermark.
    4. Facebook Broadcast: Publishes the combined visual post to Facebook Page.
    5. Database & Archive: Persists post record and updates backup snapshot.
    """
    pipeline_start = time.time()
    add_log("=== AUTO-PILOT PIPELINE INITIATED ===", "INFO", "PIPELINE_START")
    
    # Step 1: Determine Topic
    if not topic:
        add_log("Searching live trends via Trend Radar...", "INFO", "PIPELINE_TREND")
        topic = get_single_hottest_topic()
        
    add_log(f"Topic Selected: {topic}", "INFO", "PIPELINE_TOPIC")
    
    # Step 2: Content Generation
    add_log("Crafting viral hook and storytelling body via AI...", "INFO", "PIPELINE_AI")
    language = get_setting("content_language", "Bengali & English Mixed")
    content_data = generate_viral_post(topic=topic, pillar=pillar, persona=persona, language=language)
    
    full_text = content_data.get("full_post", f"{content_data.get('hook', '')}\n\n{content_data.get('body', '')}")
    image_prompt = content_data.get("image_prompt", f"Cinematic visual concept for {topic}")
    
    # Step 3: Image Generation
    add_log(f"Synthesizing visual graphic for prompt: {image_prompt[:40]}...", "INFO", "PIPELINE_IMG")
    brand = get_setting("brand_name", "PiyushSocial AI")
    img_res = generate_ai_image(prompt=image_prompt, brand_watermark=brand)
    
    local_img_path = img_res.get("local_path")
    web_img_url = img_res.get("url")
    
    # Step 4: Publish to Facebook Page
    add_log("Publishing media to Facebook Page via Graph API...", "INFO", "PIPELINE_FB")
    fb_res = publish_to_facebook(message=full_text, local_image_path=local_img_path)
    
    fb_post_id = fb_res.get("post_id", "demo_mode_id")
    status = "published" if fb_res.get("success") else "failed"
    
    # Step 5: Save to SQLite Database
    post_id = save_post(
        topic=topic,
        hook=content_data.get("hook", ""),
        content=full_text,
        hashtags=content_data.get("hashtags", ""),
        image_url=web_img_url,
        local_image_path=local_img_path,
        fb_post_id=fb_post_id,
        status=status,
        niche=pillar
    )
    
    # Step 6: Trigger automatic local database snapshot
    try:
        create_local_backup()
    except Exception as e:
        print("Backup notice:", e)
        
    duration = round(time.time() - pipeline_start, 2)
    add_log(f"=== PIPELINE COMPLETED IN {duration}s [Post ID #{post_id}] ===", "SUCCESS", "PIPELINE_COMPLETE")
    
    return {
        "success": True,
        "post_id": post_id,
        "topic": topic,
        "hook": content_data.get("hook", ""),
        "content": full_text,
        "image_url": web_img_url,
        "fb_post_id": fb_post_id,
        "fb_status": fb_res,
        "duration_sec": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
