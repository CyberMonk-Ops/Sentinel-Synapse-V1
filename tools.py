import os
import json
import logging
import requests
import re
import yt_dlp
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
TRACKING_FILE = "tracking.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# =========================================
#  MODULE 1: THE PRICE SCRAPER (NUCLEAR)
# =========================================
def check_price(url):
    """
    Scrapes title and price using Meta Tags, Classes, and Regex.
    """
    try:
        session = requests.Session()
        # Clean URL (Remove tracking parameters for better matching)
        if "flipkart" in url and "?" in url:
            url = url.split("?")[0]
            
        response = session.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        
        price = "Not Found"
        title = "Unknown Product"

        # --- A. TITLE EXTRACTION ---
        if soup.title:
            title = soup.title.string.strip()[:50] + "..."
        
        # Specific Site Logic for Title
        try:
            if "amazon" in url:
                t = soup.find(id="productTitle")
                if t: title = t.get_text().strip()[:50] + "..."
            elif "flipkart" in url:
                # Common Flipkart Title Classes
                for cls in ["VU-ZEz", "B_NuCI", "yhB1nd"]:
                    t = soup.find(class_=cls)
                    if t: 
                        title = t.get_text().strip()[:50] + "..."
                        break
        except: pass

        # --- B. PRICE EXTRACTION ---
        # Strategy 1: Meta Tags (The most reliable)
        meta_candidates = [
            ("meta", {"property": "og:price:amount"}),
            ("meta", {"itemprop": "price"}),
            ("div", {"class": "Nx9bqj"}),       # Flipkart Current
            ("div", {"class": "_30jeq3"}),      # Flipkart Old
            ("span", {"class": "a-price-whole"}) # Amazon
        ]

        for tag, attrs in meta_candidates:
            element = soup.find(tag, attrs)
            if element:
                raw_price = element.get("content") if tag == "meta" else element.get_text()
                if raw_price:
                    # Clean the price string (Remove letters, keep digits)
                    price = "₹" + re.sub(r"[^\d]", "", raw_price)
                    break
        
        # Strategy 2: Regex Fallback (Look for ₹ pattern)
        if price == "Not Found" or price == "₹":
            matches = soup.find_all(string=re.compile(r"₹\s*[\d,]+"))
            for match in matches:
                clean_text = match.strip()
                if len(clean_text) < 20 and any(char.isdigit() for char in clean_text):
                    price = clean_text
                    break

        return title, price

    except Exception as e:
        return None, f"Error: {str(e)}"

# =========================================
#  MODULE 2: DATABASE MANAGER (JSON)
# =========================================
def load_data():
    if not os.path.exists(TRACKING_FILE):
        return {}
    try:
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_to_tracker(chat_id, url, title, price):
    db = load_data()
    chat_id = str(chat_id)
    if chat_id not in db:
        db[chat_id] = []
    
    # Check if already tracking
    for item in db[chat_id]:
        if item['url'] == url:
            return False # Already exists

    db[chat_id].append({
        "url": url,
        "title": title,
        "last_price": price
    })
    save_data(db)
    return True

# =========================================
#  MODULE 3: THE VIDEO DOWNLOADER
# =========================================
async def download_video_logic(url, chat_id, bot):
    """
    Downloads video using yt-dlp and sends it to user.
    """
    status_msg = await bot.send_message(chat_id, text="⬇️ **Sentinel is ripping stream...**", parse_mode='Markdown')
    
    # Ensure directory exists
    if not os.path.exists('downloads'): 
        os.makedirs('downloads')

    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'geo_bypass': True,
        'quiet': True,
        'no_warnings': True,
        # 'cookiefile': 'cookies.txt', # Uncomment if you have cookies for age-gated stuff
    }

    file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            video_title = info.get('title', 'Video')

        await bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="⬆️ **Uploading to Telegram...**")

        with open(file_path, 'rb') as video_file:
            await bot.send_video(
                chat_id=chat_id, 
                video=video_file, 
                caption=f"✅ **{video_title}**\n\n*Securely Archived by Sentinel.*",
                read_timeout=300, 
                write_timeout=300
            )

    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text=f"❌ **Download Failed:** {str(e)[:100]}")
    
    finally:
        # Cleanup
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except: pass


def get_video_metadata(url):
    """
    Extracts Title, Description, and Tags using yt-dlp (Fast, No Download).
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True, # CRITICAL: Do not download video
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Construct a clean text block for the AI
            metadata = (
                f"Title: {info.get('title')}\n"
                f"Channel: {info.get('uploader')}\n"
                f"Duration: {info.get('duration_string')}\n"
                f"Description: {info.get('description')[:1500]}..." # Limit to 1500 chars so we don't crash memory
            )
            return metadata
    except Exception as e:
        return None



def get_trending_report():
    """
    Scrapes the top 10 trending videos from YouTube.
    Returns a text block for the Brain to analyze.
    """
    TRENDING_URL =  "ytsearch15:India News viral"     #"https://www.youtube.com/feed/trending"
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': True, # CRITICAL: Don't download, just list titles
        'playlistend': 10,    # Only top 10
        'no_warnings': True,
        'http_headers': {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9", "Referer": "https://www.google.com/"}
    }

    try:
        data_points = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info from the trending feed
            info = ydl.extract_info(TRENDING_URL, download=False)
            
            if 'entries' in info:
                for i, entry in enumerate(info['entries']):
                    title = entry.get('title')
                    views = entry.get('view_count', 'N/A')
                    channel = entry.get('uploader')
                    data_points.append(f"{i+1}. {title} | Channel: {channel}")
        
        # Join into a single string
        return "\n".join(data_points)

    except Exception as e:
        return f"Error scouting trends: {e}"
