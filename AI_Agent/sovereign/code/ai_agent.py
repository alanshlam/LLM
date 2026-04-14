#!/home/llm/miniconda3/bin/python3

import os
import sys
import time
import base64
import requests
import whisper
import mailbox
import email.utils
import csv
import re
from pathlib import Path
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# --- CONFIGURATION ---
load_dotenv(Path(__file__).parent / ".env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AUDIO_TMP_PATH = "/tmp/daily_news_flash.mp3"

# Local Data Paths
MBOX_PATH = os.getenv("MBOX_PATH", "inbox.mbox")
SCHEDULE_PATH = os.getenv("SCHEDULE_PATH", "schedule.md")
TASKS_PATH = os.getenv("TASKS_PATH", "tasks.md")
EXPENSES_PATH = os.getenv("EXPENSES_PATH", "expenses.csv")

# Camera & Models
CCTV_IMAGE_URL = os.getenv("CCTV_IMAGE_URL", "https://tdcctv.data.one.gov.hk/TC001F.JPG")
CCTV_NAME = os.getenv("CCTV_NAME", "HK TM-CLK Tunnel")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")
OLLAMA_SUMMARY_MODEL = os.getenv("OLLAMA_SUMMARY_MODEL", "gemma4:31b")

# News RSS Feeds (Defaults provided if not in .env)
AI_FEED_URL = os.getenv("AI_FEED_URL", "https://techcrunch.com/category/artificial-intelligence/feed/")
CYBER_FEED_URL = os.getenv("CYBER_FEED_URL", "https://feeds.feedburner.com/TheHackersNews")

# --- DATA FETCHING FUNCTIONS ---

def read_local_file(filepath):
    if not os.path.exists(filepath): return "No data provided."
    with open(filepath, 'r') as f: return f.read().strip()

def get_expenses_summary(filepath):
    if not os.path.exists(filepath): return "No recent expense data."
    try:
        total = 0.0
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += float(row['Amount'])
        return f"Total spent recently: ${total:.2f}"
    except Exception as e:
        return f"Expense error: {e}"

def get_latest_emails(filepath, limit=5):
    if not os.path.exists(filepath): 
        return "No mailbox found.", "<i>No mailbox found.</i>"
    try:
        mbox = mailbox.mbox(filepath)
        messages = list(mbox)
        if not messages: 
            return "Inbox is empty.", "<i>Inbox is empty.</i>"
        
        latest_msgs = reversed(messages[-limit:])
        raw_context =[]
        display_lines =[]
        
        for msg in latest_msgs:
            sender = msg.get('From', 'Unknown')
            subject = msg.get('Subject', 'No Subject')
            real_name, email_addr = email.utils.parseaddr(sender)
            display = real_name if real_name else email_addr
            
            body_snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            body_snippet = " ".join(body.split())[:150]
                            break
                        except: pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    body_snippet = " ".join(body.split())[:150]
                except: pass
            
            raw_context.append(f"From: {display} | Subject: {subject} | Body: {body_snippet}...")
            display_lines.append(f"▪️ <b>{display}</b>: {subject}")
            
        return "\n".join(raw_context), "\n".join(display_lines)
    except Exception as e: 
        return f"Error reading mailbox: {e}", "<i>Error reading mailbox.</i>"

def get_nvda_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/NVDA?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10).json()
        meta = res['chart']['result'][0]['meta']
        price, prev = meta['regularMarketPrice'], meta['previousClose']
        char = "📈" if price >= prev else "📉"
        return f"NVDA: ${price:.2f} ({char} {price-prev:+.2f})"
    except: return "NVDA: Data unavailable"

def get_weather():
    cities = {"New York": (40.71, -74.00), "London": (51.50, -0.12), "Hong Kong": (22.31, 114.17)}
    reports =[]
    try:
        for city, (lat, lon) in cities.items():
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            res = requests.get(url, timeout=10).json()
            reports.append(f"{city}: {res['current_weather']['temperature']}°C")
        return " | ".join(reports)
    except Exception as e: 
        return "Weather unavailable"

def get_traffic_condition(image_url, name, model):
    print(f"🚦 Analyzing traffic from {name}...")
    try:
        response = requests.get(image_url, timeout=15)
        img_b64 = base64.b64encode(response.content).decode('utf-8')
        payload = {
            "model": model,
            "prompt": "Analyze this traffic camera image. Describe the traffic conditions in one short sentence.",
            "stream": False,
            "images": [img_b64]
        }
        res = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=60).json()
        return f"{name}: {res.get('response', 'Unable to analyze').strip()} <a href='{image_url}'>[Cam]</a>"
    except: return f"{name}: Data unavailable. <a href='{image_url}'>[Cam]</a>"

def clean_html(raw_html):
    """Utility to strip HTML tags from RSS descriptions"""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def fetch_rss_news(category, feed_url, max_results=5):
    """Fetches and parses standard RSS feeds to get clean, reliable news."""
    print(f"📡 Fetching {category} News from {feed_url}...")
    results =[]
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(feed_url, headers=headers, timeout=15)
        root = ET.fromstring(response.content)
        
        # Grab the latest items up to max_results
        for item in root.findall('.//item')[:max_results]:
            title = item.findtext('title', default='No Title')
            link = item.findtext('link', default='#')
            description = item.findtext('description', default='')
            
            # Clean HTML tags and truncate for the AI context
            clean_desc = clean_html(description)[:200]
            
            results.append({
                "title": title,
                "body": clean_desc,
                "url": link
            })
            
        print(f"✅ Found {len(results)} articles for {category}.")
    except Exception as e:
        print(f"⚠️ RSS fetch failed for {category}: {e}")
    return results

def process_audio_news():
    print("🎙️ Fetching audio news flash...")
    try:
        response = requests.get("https://feeds.npr.org/500005/podcast.xml", timeout=20)
        root = ET.fromstring(response.content)
        item = root.find(".//item")
        audio_url = item.find("enclosure").attrib['url']
        
        audio_data = requests.get(audio_url, timeout=60)
        with open(AUDIO_TMP_PATH, 'wb') as f: f.write(audio_data.content)
        
        model = whisper.load_model("base")
        result = model.transcribe(AUDIO_TMP_PATH)
        if os.path.exists(AUDIO_TMP_PATH): os.remove(AUDIO_TMP_PATH)
        return result['text'], audio_url
    except: return None, None

# --- AI REASONING & SUMMARIZATION ---

def generate_private_briefing(schedule, tasks, expenses, weather, emails, model):
    print(f"🧠 Generating Private Briefing ({model})...")
    prompt = f"""You are an elite, private AI executive assistant. 
    Analyze the user's private data and provide a short, punchy morning briefing.

    DATA CONTEXT:
    Weather: {weather}
    Schedule: {schedule}
    Tasks: {tasks}
    Expenses: {expenses}
    Emails: {emails}

    INSTRUCTIONS: Provide exactly 4 short bullet points. Do not use bold tags, just emojis.
    1. 🗓️ Schedule: Summarize the day's pacing in one sentence. Warn them if an event conflicts with the weather.
    2. ✅ Priority: Suggest EXACTLY TWO tasks to focus on today based on logic.
    3. 💸 Finance: Give a 1-sentence friendly observation about their recent spending total.
    4. 📧 Inbox Action: Give a 1-sentence actionable advice on the latest emails (e.g., flag urgent ones, suggest replies, or warn about deadlines).
    """
    try:
        res = requests.post("http://127.0.0.1:11434/api/generate", 
                            json={"model": model, "prompt": prompt, "stream": False, "options": {"num_ctx": 4096}}, 
                            timeout=120).json()
        return res.get("response", "").strip()
    except Exception as e: 
        print(f"❌ Private briefing error: {e}")
        return "Private briefing generation failed."

def generate_news_briefing(ai_news, cyber_news, audio_text, audio_url, model):
    print(f"🤖 Generating News Briefing ({model})...")
    
    ai_ctx = "\n".join([f"ID: AI_{i} | {n.get('title', 'No Title')} | {n.get('body', '')[:150]}" for i, n in enumerate(ai_news)])
    cy_ctx = "\n".join([f"ID: CY_{i} | {n.get('title', 'No Title')} | {n.get('body', '')[:150]}" for i, n in enumerate(cyber_news)])

    prompt = f"""You are an elite news analyst. Summarize the provided news strictly following the format.

    AUDIO TRANSCRIPT:
    {audio_text if audio_text else 'None available'}

    AI NEWS:
    {ai_ctx}

    CYBER NEWS:
    {cy_ctx}

    STRICT INSTRUCTIONS:
    1. Output exactly THREE sections:
       - "📻 GLOBAL AUDIO FLASH" (Summarize the AUDIO TRANSCRIPT into exactly 3 short bullets)
       - "🤖 AI BREAKTHROUGHS" (Exactly 3 bullets summarizing AI NEWS)
       - "🛡️ CYBERSECURITY" (Exactly 3 bullets summarizing CYBER NEWS)
    2. Each news/cyber bullet must be exactly 1 sentence.
    3. End each AI/Cyber bullet with [[LNK_ID]] (e.g., [[LNK_AI_0]]).
    """
    try:
        payload = {
            "model": model, 
            "prompt": prompt, 
            "stream": False,
            "options": {"num_ctx": 8192} 
        }
        res = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=180)
        res.raise_for_status() 
        summary = res.json().get("response", "")
        
        # Inject formatted Audio Link
        if audio_url:
            summary = summary.replace("📻 GLOBAL AUDIO FLASH", f'📻 <b>GLOBAL AUDIO FLASH</b>\nSource: <a href="{audio_url}">NPR News Now</a>')

        # Safely Inject Links for web articles
        for i, a in enumerate(ai_news): 
            link = a.get("url") or a.get("href") or "#"
            summary = summary.replace(f"[[LNK_AI_{i}]]", f' <a href="{link}">[Read]</a>')
            
        for i, a in enumerate(cyber_news): 
            link = a.get("url") or a.get("href") or "#"
            summary = summary.replace(f"[[LNK_CY_{i}]]", f' <a href="{link}">[Read]</a>')
            
        return summary
    except Exception as e: 
        print(f"❌ News summarization error: {e}")
        return "News summarization failed."

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    return requests.post(url, json=payload, timeout=20)

def main():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: sys.exit(1)

    # 1. Gather Public Data
    nvda = get_nvda_price()
    weather = get_weather()
    traffic = get_traffic_condition(CCTV_IMAGE_URL, CCTV_NAME, OLLAMA_VISION_MODEL)
    
    # 2. Gather Private Data
    schedule = read_local_file(SCHEDULE_PATH)
    tasks = read_local_file(TASKS_PATH)
    expenses = get_expenses_summary(EXPENSES_PATH)
    emails_context, emails_display = get_latest_emails(MBOX_PATH, limit=5)

    # 3. Gather News (Now via configurable RSS feeds!)
    audio_text, audio_url = process_audio_news()
    ai_news = fetch_rss_news("AI", AI_FEED_URL, 5)
    cyber_news = fetch_rss_news("Cybersecurity", CYBER_FEED_URL, 5)

    # 4. LLM Generation
    private_briefing = generate_private_briefing(schedule, tasks, expenses, weather, emails_context, OLLAMA_SUMMARY_MODEL)
    news_briefing = generate_news_briefing(ai_news, cyber_news, audio_text, audio_url, OLLAMA_SUMMARY_MODEL)

    # 5. Construct Final Mobile-Friendly Dashboard
    final_message = f"""<b>📱 THE SOVEREIGN AGENT</b>
<i>Your Zero-Cloud Daily Dashboard</i>

<b>🌍 PUBLIC RADAR</b>
💹 {nvda}
☁️ {weather}
🚗 {traffic}

<b>👤 PRIVATE BRIEFING</b>
{private_briefing}

<b>✉️ LATEST EMAILS:</b>
{emails_display}

<b>📰 GLOBAL INTEL</b>
{news_briefing}
"""
    
    print("📤 Pushing to Mobile Device...")
    if send_telegram(final_message): print("✅ Dashboard Delivered!")
    else: print("❌ Delivery Failed.")

if __name__ == "__main__":
    main()



