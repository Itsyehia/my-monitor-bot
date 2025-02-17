import asyncio
import requests
import atexit
import time
import threading
import logging
from flask import Flask, render_template, jsonify
from telegram import Bot as TelegramBot
from datetime import datetime

# === Global log store ===
logs = []  # List to store log messages

# === Custom logging handler to capture logs in memory ===
class InMemoryLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        logs.append(msg)

# === Configure logging ===
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)
# Attach the in-memory handler
in_memory_handler = InMemoryLogHandler()
in_memory_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(in_memory_handler)

# === Configuration ===
API_URL = "http://193.227.14.58/api/student-registration-courses?studentId=20215051"
BEARER_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDIxNTA1MSIsImF1dGgiOiJST0xFX1NUVURFTlQiLCJleHAiOjE3Mzk4MTczNDd9.JdVsCWqbhgUl5VbAxaYuiQUmamIqM-kcsRRtP8-LvVjuSsJBRK42xicDMdZ5DD8GTRRy1OXYNUujxnCSdDF2Gg"
TELEGRAM_TOKEN = "7947829276:AAERvSxeiofBVuIyL_6lzhokxxUEPJo_00Y"
CHAT_ID = "451246357"

CHECK_INTERVAL = 60

# === Initialize Telegram Bot ===
bot = TelegramBot(token=TELEGRAM_TOKEN)

# === Flask App Initialization ===
app = Flask(__name__)

# === Async Function to Send Telegram Message ===
async def send_telegram_message(message):
    try:
        logger.info("🚀 Sending message to Telegram...")
        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info("✅ Message sent to Telegram!")
    except Exception as e:
        logger.error(f"❌ Telegram API Error: {e}")

# === Send Message on Exit ===
def on_exit():
    asyncio.run(send_telegram_message("⚠️ Bot has stopped running. Please check your server."))

atexit.register(on_exit)

# === Check Registration Status ===
def check_registration_status():
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get('responseCode') != -1:
            asyncio.run(send_telegram_message("🚀 Registration is NOW OPEN! Hurry up!"))
            return True
        logger.info("Registration still closed.")
        return False
    except requests.RequestException as e:
        logger.error(f"API Request Error: {e}")
        return False

# === Monitoring Function (runs in background) ===
def monitor_registration():
    logger.info("🚀 Starting Registration Monitor Bot...")
    asyncio.run(send_telegram_message("🚀 Bot Started! Monitoring every 60 seconds."))
    while True:
        if check_registration_status():
            asyncio.run(send_telegram_message("✅ Registration Just Opened!"))
            break
        time.sleep(CHECK_INTERVAL)

# === Flask Routes ===

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start")
def start_monitoring():
    # Start the monitoring in a background thread so the server remains responsive.
    monitor_thread = threading.Thread(target=monitor_registration)
    monitor_thread.daemon = True
    monitor_thread.start()
    return "Monitoring started in the background!"

@app.route("/logs")
def get_logs():
    # Return the logs as JSON.
    # Optionally, you can limit the number of log entries returned.
    return jsonify(logs)

if __name__ == "__main__":
    # Listen on all interfaces for OpenShift
    app.run(host="0.0.0.0", port=8080, debug=True)
