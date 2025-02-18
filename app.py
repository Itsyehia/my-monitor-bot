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
REGISTRATION_API_URL = "http://193.227.14.58/api/student-registration-courses?studentId=20215051"
COURSES_API_URL = "http://193.227.14.58/api/student-courses?size=150&studentId.equals=20215051&includeWithdraw.equals=true&grade.specified=false"
BEARER_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDIxNTA1MSIsImF1dGgiOiJST0xFX1NUVURFTlQiLCJleHAiOjE3Mzk5NjU5Mjl9.u4jDVhkrcxZ_UXVO54PyyIpghO8lbU1Qm0vyxQMgYxBOhRgMCkgpyjR1avu4aylRxusFr4MSpvDxifA5y8EqIA"
TELEGRAM_TOKEN = "7947829276:AAERvSxeiofBVuIyL_6lzhokxxUEPJo_00Y"
CHAT_ID = "451246357"

CHECK_INTERVAL = 60  # Check every 60 seconds

# === Initialize Telegram Bot ===
bot = TelegramBot(token=TELEGRAM_TOKEN)

# === Store Previous Course Statuses and Registration Status ===
previous_courses = {}
registration_open_alerted = False

# === Async Function to Send Telegram Message ===
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

# === Fetch Current Courses without Grades ===
def fetch_courses():
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(COURSES_API_URL, headers=headers)
        response.raise_for_status()
        courses = response.json()
        return {course['id']: course for course in courses}
    except requests.RequestException as e:
        logger.error(f"API Request Error (Courses): {e}")
        return {}

# === Fetch Registration Status ===
def fetch_registration_status():
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(REGISTRATION_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('responseCode') != -1  # True if registration is open
    except requests.RequestException as e:
        logger.error(f"API Request Error (Registration): {e}")
        return False

# === Check for Course Updates (Grades) ===
async def check_course_updates():
    global previous_courses
    current_courses = fetch_courses()

    for course_id, course in current_courses.items():
        if course_id in previous_courses:
            prev_course = previous_courses[course_id]
            if prev_course['grade'] is None and course.get('grade') is not None:
                course_name = course['course']['name']
                grade = course['grade']
                await send_telegram_message(
                    f"🎉 Course '{course_name}' has been updated with grade: {grade}"
                )
        else:
            logger.info(f"New course without grade found: {course['course']['name']}")

    previous_courses = current_courses

# === Check for Registration Updates ===
async def check_registration_updates():
    global registration_open_alerted
    registration_open = fetch_registration_status()

    if registration_open and not registration_open_alerted:
        await send_telegram_message("🚀 Registration is NOW OPEN! Hurry up!")
        registration_open_alerted = True
    elif not registration_open and registration_open_alerted:
        registration_open_alerted = False
        logger.info("Registration is closed.")

# === Main Execution Loop ===
async def main():
    logger.info("🚀 Starting Combined Monitor Bot...")
    await send_telegram_message("🚀 Bot Started! Monitoring registration and courses with no grades every 60 seconds.")

    while True:
        await check_course_updates()
        await check_registration_updates()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
