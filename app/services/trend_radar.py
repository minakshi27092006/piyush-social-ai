import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Any
from app.database import add_log

TRENDS_FEEDS = {
    "world": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "tech": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
    "bd": "https://news.google.com/rss?hl=bn&gl=BD&ceid=BD:bn",
    "in": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "google_trends_us": "https://trends.google.com/trending/rss?geo=US",
    "google_trends_in": "https://trends.google.com/trending/rss?geo=IN"
}

FALLBACK_TRENDS = [
    {"title": "OpenAI and Google Release Next-Gen Autonomous AI Agents", "category": "AI & Tech", "source": "Tech Radar"},
    {"title": "Top Productivity Habits of the World's Highest Performing Creators", "category": "Motivation & Growth", "source": "Success Insights"},
    {"title": "The Rise of Humanoid Robots and What It Means for Future Jobs", "category": "Future & Robotics", "source": "Futurism"},
    {"title": "How Small Creators are Building Million-Dollar Personal Brands in 2026", "category": "Creator Economy", "source": "Social Media Trends"},
    {"title": "Revolutionary Breakthroughs in Clean Energy and Smart Cities", "category": "Science & Innovation", "source": "Global Science"}
]

def fetch_trending_topics(region: str = "world", limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch live trending topics from Google Trends or Google News RSS."""
    feed_url = TRENDS_FEEDS.get(region, TRENDS_FEEDS["world"])
    topics = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(feed_url, headers=headers, timeout=8)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            
            for item in items[:limit]:
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubDate")
                desc_elem = item.find("description")
                
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled Topic"
                # Strip source suffix if present (e.g. " - TechCrunch")
                clean_title = title.split(" - ")[0] if " - " in title else title
                
                topics.append({
                    "title": clean_title,
                    "raw_title": title,
                    "link": link_elem.text if link_elem is not None else "",
                    "published": pub_elem.text if pub_elem is not None else "",
                    "source": "Google Live RSS",
                    "category": region.upper()
                })
                
        if topics:
            add_log(f"Successfully fetched {len(topics)} live trends from {region.upper()}", "INFO", "TREND_RADAR")
            return topics
            
    except Exception as e:
        add_log(f"Trend Radar fallback triggered due to: {str(e)}", "WARNING", "TREND_RADAR")
        
    # Return curated fallbacks if network RSS fails
    return FALLBACK_TRENDS[:limit]

def get_single_hottest_topic(category: str = "tech") -> str:
    """Returns the top 1 hottest topic string for immediate auto-posting."""
    trends = fetch_trending_topics(category, limit=3)
    if trends:
        return trends[0]["title"]
    return "The Future of Artificial Intelligence and Human Creativity in 2026"
