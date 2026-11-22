# 🚀 PiyushSocial AI - Autonomous Facebook Page Manager & World-Class Content Studio

An autonomous, 24/7 AI-powered Facebook Page Management Platform and Elite Content Studio. Operates seamlessly on both **PC and Mobile**, with automated background publishing, AI visual synthesis, intelligent community engagement, and offline master database backups on your laptop.

---

## 🌟 Key Features

1. **🔥 Live Trend Radar:**
   - Real-time Google Trends & Google News integration.
   - Automatically detects viral news and trending topics across World, Tech, and Regional categories.

2. **🤖 Elite AI Copywriting Engine (Gemini 2.5):**
   - **Stop-The-Scroll Hooks:** High-retention opening lines that halt scrolling.
   - **Content Pillars:** Switch between Educational, Storytelling, Viral News, Motivation, and Interactive Polls.
   - **Multi-Persona:** Professional, Witty, Charismatic, or Inspiring voice in Bengali, Banglish, or English.

3. **🎨 AI Visual Synthesis & Auto-Branding (Pollinations AI + Pillow):**
   - 100% Free Flux/SD photorealistic 8K image generation.
   - Automatic luxury glassmorphic watermark overlay with your Page or Brand Name.

4. **⏱️ 24/7 Autonomous Auto-Pilot Pipeline (Post Even When Laptop is OFF):**
   - Set intervals: **30 Mins, 1 Hour, 2 Hours, 4 Hours**.
   - Built-in GitHub Actions & Render blueprints execute in the cloud even when your PC is powered off.

5. **📱 Mobile & PC Unified Dashboard (PWA):**
   - Works in desktop browsers and installs as a native-feel mobile app on Android/iOS via *"Add to Home screen"*.
   - Real-time live countdown timer, activity stream logs, and 1-click publishing.

6. **💾 Laptop Master Backup & Offline Security:**
   - Your laptop acts as the permanent offline repository.
   - Automatic SQLite database snapshots, image archiving, and 1-click master ZIP backup export.

7. **🎬 Reels & Video Script Lab:**
   - Generates 45-second viral video scripts with camera directions, voiceover, and audio trend cues.

---

## 🚀 How to Run Locally on Your PC

### 1. Quick 1-Click Launch:
Double-click `start_app.bat` inside `d:\FACEBOOK`.

### 2. Manual Terminal Launch:
```powershell
cd d:\FACEBOOK
.\.venv\Scripts\python.exe run_server.py
```

Open your browser:
* **💻 On PC:** `http://localhost:8000`
* **📱 On Mobile Phone:** Connect to the same Wi-Fi, open the displayed LAN IP (e.g. `http://192.168.1.X:8000`), then tap **"Add to Home screen"** to install as a mobile app!

---

## ☁️ Running 24/7 Even When Laptop is Powered Off

You have two 100% FREE cloud options:

### Option A: GitHub Actions (Recommended - 100% Free)
1. Push this folder to a private or public GitHub repository.
2. In GitHub, go to **Settings > Secrets and variables > Actions**.
3. Add these repository secrets:
   - `GEMINI_API_KEY`: Your free Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikey)
   - `FACEBOOK_PAGE_ID`: Your Facebook Page ID
   - `FACEBOOK_PAGE_ACCESS_TOKEN`: Your Meta Graph API Page Token
4. The workflow in `.github/workflows/auto_post_cron.yml` will automatically run every 1 hour, generate posts, and commit the database snapshots back to your repo!

### Option B: Render.com Cloud Web Service
1. Connect your GitHub repository to [Render.com](https://render.com).
2. It will automatically detect `render.yaml` and launch a 24/7 cloud server with a free public `https://...` link for your phone!

---

## 🔑 Getting Free API Keys

1. **Google Gemini API Key (100% Free):**
   - Visit [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   - Click "Create API Key" and copy it into the app's Settings tab.

2. **Facebook Page Access Token:**
   - Go to [Meta for Developers Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Select your Facebook Page and grant `pages_manage_posts` and `pages_read_engagement` permissions.
   - Paste the Page ID and Token into the Settings tab.

---

## 📂 Project Structure
```
d:\FACEBOOK\
├── app\
│   ├── config.py              # Configuration & directories
│   ├── database.py            # SQLite database & backup snapshots
│   ├── pipeline.py            # Master Autonomous Pipeline Engine
│   ├── main.py                # FastAPI server & REST endpoints
│   ├── services\
│   │   ├── trend_radar.py     # Live Google Trends / News RSS
│   │   ├── gemini_ai.py       # Viral copywriter & Reels generator
│   │   ├── image_generator.py # Pollinations AI & Pillow Watermarking
│   │   ├── facebook_service.py# Meta Graph API publisher
│   │   ├── scheduler_service.py # APScheduler interval engine
│   │   └── backup_service.py  # Laptop master archive packager
│   ├── static\
│   │   ├── css\custom.css     # Luxury dark cyberpunk aesthetics
│   │   ├── js\app.js          # Reactive controller & countdown timer
│   │   ├── manifest.json      # PWA mobile installation manifest
│   │   └── images\            # Stored post images
│   └── templates\
│       └── index.html         # Responsive SaaS dashboard
├── backups\                   # Permanent offline laptop backups
├── .github\workflows\         # 24/7 cloud auto-post cron pipeline
├── Dockerfile                 # Cloud deployment container
├── render.yaml                # Render cloud blueprint
├── run_server.py              # Launch script
└── start_app.bat              # 1-click Windows launcher
```
