import asyncio
import requests
import atexit
import time
from telegram import Bot as TelegramBot
import logging

# === Enable Logging for Debugging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Configuration ===
API_URL = "http://193.227.14.58/api/student-registration-courses?studentId=20215051"
BEARER_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDIxNTA1MSIsImF1dGgiOiJST0xFX1NUVURFTlQiLCJleHAiOjE3Mzk4MTczNDd9.JdVsCWqbhgUl5VbAxaYuiQUmamIqM-kcsRRtP8-LvVjuSsJBRK42xicDMdZ5DD8GTRRy1OXYNUujxnCSdDF2Gg"
TELEGRAM_TOKEN = "7947829276:AAERvSxeiofBVuIyL_6lzhokxxUEPJo_00Y"
CHAT_ID = "451246357"

CHECK_INTERVAL = 60

# === Initialize Telegram Bot ===
bot = TelegramBot(token=TELEGRAM_TOKEN)

# === Async Function to Send Telegram Message (using asyncio.to_thread) ===
async def send_telegram_message(message):
    try:
        logger.info("🚀 Sending message to Telegram...")
        # Wrap the synchronous call in a thread so we can await it.
        await asyncio.to_thread(bot.send_message, chat_id=CHAT_ID, text=message)
        logger.info("✅ Message sent to Telegram!")
    except Exception as e:
        logger.error(f"❌ Telegram API Error: {e}")

# === Send Message on Exit ===
def on_exit():
    asyncio.run(send_telegram_message("⚠️ Bot has stopped running. Please check your Replit session."))

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

# === Main Execution Loop ===
if __name__ == "__main__":
    logger.info("🚀 Starting Registration Monitor Bot...")
    asyncio.run(send_telegram_message("🚀 Bot Started! Monitoring every 60 seconds."))
    while True:
        if check_registration_status():
            asyncio.run(send_telegram_message("✅ Registration Just Opened!"))
            break
        time.sleep(CHECK_INTERVAL)
