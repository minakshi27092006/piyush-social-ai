import socket
import uvicorn
import sys
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000
    
    print("=" * 65)
    print(" 🚀  PIYUSH SOCIAL AI - AUTONOMOUS FACEBOOK MANAGER & CONTENT STUDIO")
    print("=" * 65)
    print(f" 💻 PC Dashboard (Local):   http://localhost:{port}")
    print(f" 📱 Mobile Phone Link:      http://{local_ip}:{port}")
    print("=" * 65)
    print(" [Tip] Open the Mobile link on your phone browser, then tap")
    print("       'Add to Home screen' to install as a Native Mobile App!")
    print("=" * 65)
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
