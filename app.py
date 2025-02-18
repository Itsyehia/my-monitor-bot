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
STUDENT_ID = "20215051"
REGISTRATION_API_URL = f"http://193.227.14.58/api/student-registration-courses?studentId={STUDENT_ID}"
GRADES_API_URL = f"http://193.227.14.58/api/student-courses?size=150&studentId.equals={STUDENT_ID}&includeWithdraw.equals=true&grade.specified=false"

BEARER_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDIxNTA1MSIsImF1dGgiOiJST0xFX1NUVURFTlQiLCJleHAiOjE3Mzk5NjU5Mjl9.u4jDVhkrcxZ_UXVO54PyyIpghO8lbU1Qm0vyxQMgYxBOhRgMCkgpyjR1avu4aylRxusFr4MSpvDxifA5y8EqIA"
TELEGRAM_TOKEN = "7947829276:AAERvSxeiofBVuIyL_6lzhokxxUEPJo_00Y"
CHAT_ID = "451246357"

CHECK_INTERVAL = 60
bot = TelegramBot(token=TELEGRAM_TOKEN)

# === Store Previous Course Data ===
previous_courses = {}

# === Async Function to Send Telegram Messages ===
async def send_telegram_message(message):
    try:
        logger.info("🚀 Sending message to Telegram...")
        await asyncio.to_thread(bot.send_message, chat_id=CHAT_ID, text=message)
        logger.info("✅ Message sent to Telegram!")
    except Exception as e:
        logger.error(f"❌ Telegram API Error: {e}")

# === Send Message on Exit ===
def on_exit():
    asyncio.run(send_telegram_message("⚠️ Bot has stopped running. Please check your session."))

atexit.register(on_exit)

# === Check Registration Status ===
def check_registration_status():
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}', 'Content-Type': 'application/json'}
    try:
        response = requests.get(REGISTRATION_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get('responseCode') != -1:
            asyncio.run(send_telegram_message("🚀 Registration is NOW OPEN! Hurry up!"))
            return True
        logger.info("📌 Registration still closed.")
        return False
    except requests.RequestException as e:
        logger.error(f"❌ API Request Error (Registration): {e}")
        return False

# === Check for Course Grade Updates ===
def check_course_updates():
    global previous_courses
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}', 'Content-Type': 'application/json'}
    
    try:
        response = requests.get(GRADES_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

        updated_courses = []
        new_courses = {}

        for course in data:
            course_name = course["course"]["name"]
            grade = course.get("grade")
            
            if course_name not in previous_courses:
                new_courses[course_name] = grade
            elif previous_courses[course_name] is None and grade is not None:
                updated_courses.append(course_name)

        previous_courses.update(new_courses)

        if updated_courses:
            for course in updated_courses:
                asyncio.run(send_telegram_message(f"🎉 Course '{course}' has been updated! Check your grades!"))
            return True
        
        logger.info("📌 No new grades released yet.")
        return False

    except requests.RequestException as e:
        logger.error(f"❌ API Request Error (Grades): {e}")
        return False

# === Main Execution Loop ===
if __name__ == "__main__":
    logger.info("🚀 Starting Registration & Course Monitor Bot...")
    asyncio.run(send_telegram_message("🚀 Bot Started! Monitoring every 60 seconds."))

    time.sleep(60)  # Wait for 1 minute before sending the "still running" message
    asyncio.run(send_telegram_message("✅ Bot is still running!"))

    while True:
        grade_updated = check_course_updates()
        registration_open = check_registration_status()
        
        if not grade_updated:
            logger.info("📌 No new grades released yet.")
        
        if not registration_open:
            logger.info("📌 Registration still closed.")

        time.sleep(CHECK_INTERVAL)
