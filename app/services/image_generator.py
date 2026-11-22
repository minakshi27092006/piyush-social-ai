import os
import urllib.parse
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.config import IMAGES_DIR
from app.database import add_log, get_setting

def generate_ai_image(prompt: str, style: str = "cinematic photorealistic 8k", 
                      brand_watermark: str = "", width: int = 1080, height: int = 1080) -> dict:
    """
    Generates an AI image using high-speed Pollinations Flux/SD engine (100% Free),
    downloads it locally, and optionally overlays brand typography watermark.
    """
    try:
        # Enhance prompt for elite social media aesthetic
        enhanced_prompt = f"{prompt}, {style}, highly detailed, vibrant colors, trending on artstation, masterpiece, award winning photography, 8k resolution"
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        
        # Pollinations.ai generates direct images via URL
        seed = int(datetime.now().timestamp()) % 100000
        image_api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
        
        # Download image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"post_img_{timestamp}.jpg"
        local_filepath = IMAGES_DIR / filename
        
        response = requests.get(image_api_url, timeout=30)
        if response.status_code == 200:
            with open(local_filepath, "wb") as f:
                f.write(response.content)
                
            # Apply watermark if enabled
            watermark_text = brand_watermark or get_setting("brand_name", "PiyushSocial AI")
            enable_watermark = get_setting("enable_watermark", "true").lower() == "true"
            
            if enable_watermark and watermark_text:
                apply_luxury_watermark(str(local_filepath), watermark_text)
                
            add_log(f"AI image generated and stored: {filename}", "SUCCESS", "IMAGE_GEN")
            
            return {
                "success": True,
                "local_path": str(local_filepath),
                "filename": filename,
                "url": f"/static/images/{filename}",
                "direct_api_url": image_api_url
            }
        else:
            add_log(f"Pollinations returned status {response.status_code}", "ERROR", "IMAGE_GEN")
            return create_fallback_graphic(prompt, watermark_text)
            
    except Exception as e:
        add_log(f"Image generation exception: {str(e)}", "ERROR", "IMAGE_GEN")
        return create_fallback_graphic(prompt, brand_watermark)

def apply_luxury_watermark(image_path: str, watermark_text: str):
    """Overlays an elegant semi-transparent modern glassmorphic badge at the bottom."""
    try:
        with Image.open(image_path).convert("RGBA") as base:
            # Create overlay for gradient/badge
            overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            w, h = base.size
            # Bottom banner
            banner_height = 80
            draw.rectangle(
                [(0, h - banner_height), (w, h)],
                fill=(10, 15, 29, 210) # Sleek dark glass effect
            )
            
            # Subtle accent line
            draw.line([(0, h - banner_height), (w, h - banner_height)], fill=(56, 189, 248, 200), width=3)
            
            # Text rendering
            font_size = 28
            try:
                # Windows system font
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
                
            badge_text = f"✨ {watermark_text.upper()}  |  AI INSIGHTS"
            draw.text((30, h - banner_height + 25), badge_text, fill=(255, 255, 255, 240), font=font)
            
            # Composite
            watermarked = Image.alpha_composite(base, overlay).convert("RGB")
            watermarked.save(image_path, "JPEG", quality=95)
            
    except Exception as e:
        print(f"Watermark notice: {e}")

def create_fallback_graphic(prompt: str, brand: str = "PiyushSocial AI") -> dict:
    """Generates an aesthetic modern dark gradient canvas in case of network issue."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fallback_{timestamp}.jpg"
    local_path = IMAGES_DIR / filename
    
    img = Image.new("RGB", (1080, 1080), color=(15, 23, 42)) # Deep slate
    draw = ImageDraw.Draw(img)
    
    # Modern gradient lines & circles
    draw.ellipse([(100, 100), (980, 980)], outline=(56, 189, 248), width=4)
    draw.ellipse([(250, 250), (830, 830)], outline=(168, 85, 247), width=3)
    
    try:
        font = ImageFont.truetype("arial.ttf", 36)
        small_font = ImageFont.truetype("arial.ttf", 26)
    except:
        font = ImageFont.load_default()
        small_font = font
        
    title = prompt[:50] + "..." if len(prompt) > 50 else prompt
    draw.text((120, 500), f"🔥 {title}", fill=(255, 255, 255), font=font)
    draw.text((120, 580), f"Powered by {brand}", fill=(148, 163, 184), font=small_font)
    
    img.save(local_path, "JPEG", quality=90)
    return {
        "success": True,
        "local_path": str(local_path),
        "filename": filename,
        "url": f"/static/images/{filename}",
        "direct_api_url": ""
    }
