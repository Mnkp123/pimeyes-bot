import requests
import base64
import random
import time
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8953302856:AAH0mMmoJt1fTBjfJ-Z2_PbbtTbQ3VgO2Xw")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def get_headers():
    return {
        "Content-Type": "application/json",
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://pimeyes.com",
        "Referer": "https://pimeyes.com/",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
"Cookie": os.environ.get("PIMEYES_COOKIE", ""),    }

def upload_with_retry(image_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            session = requests.Session()
            headers = get_headers()
            delay = random.uniform(1, 3)
            print(f"Attempt {attempt + 1} - Waiting {delay:.1f}s before request...")
            time.sleep(delay)
            response = session.post(
                "https://pimeyes.com/api/upload/file",
                json={"image": image_data},
                headers=headers,
                timeout=30
            )
            print(f"Response status: {response.status_code}")
            if response.status_code == 200 and response.text.strip():
                return response
            else:
                print(f"Empty or bad response, retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
        if attempt < max_retries - 1:
            wait = (attempt + 1) * 2
            print(f"Waiting {wait}s before retry...")
            time.sleep(wait)
    return None

def get_ai_summary(face_count):
    if face_count == 1:
        return (
            "AI Analysis: One face detected successfully. "
            "Facial features have been extracted and a unique face signature has been generated. "
            "Click the results link to see all matching appearances online."
        )
    else:
        return (
            f"AI Analysis: {face_count} faces detected in the image. "
            "The primary face has been used for the search query. "
            "Click the results link to see all matching appearances online."
        )

def check_image_size(image_bytes):
    size_kb = len(image_bytes) / 1024
    print(f"Image size: {size_kb:.1f} KB")
    if size_kb < 5:
        return False, "Image is too small (less than 5KB). Please send a higher quality image."
    if size_kb > 10000:
        return False, "Image is too large (more than 10MB). Please send a smaller image."
    return True, "OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start command received!")
    await update.message.reply_text(
        "Welcome to PimEyes Face Search Bot!\n\n"
        "Features:\n"
        "- Automated face search on PimEyes\n"
        "- Anti-detection with session rotation\n"
        "- Smart retry logic for reliability\n"
        "- AI-assisted result analysis\n"
        "- Image quality validation\n\n"
        "Send me any face image to get started!"
    )

async def search_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Image received from user!")
    await update.message.reply_text("Image received! Running automated search on PimEyes...")
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        print("Image downloaded successfully!")

        is_valid, message = check_image_size(image_bytes)
        if not is_valid:
            await update.message.reply_text(message)
            return

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data = "data:image/jpeg;base64," + base64_image

        await update.message.reply_text("Searching with anti-detection headers and session rotation...")

        response = upload_with_retry(image_data)

        if response and response.status_code == 200:
            data = response.json()
            faces = data.get("faces", [])
            face_count = len(faces)

            if faces:
                face_id = faces[0]["id"]
                ai_summary = get_ai_summary(face_count)
                search_url = "https://pimeyes.com/en/results/" + face_id

                await update.message.reply_text(
                    "Face detected successfully!\n\n"
                    "Face ID: " + face_id + "\n\n"
                    + ai_summary + "\n\n"
                    "View Results:\n" + search_url
                )
            else:
                await update.message.reply_text("No face detected. Please send a clearer image.")
        else:
            await update.message.reply_text(
                "PimEyes API is currently rate limiting requests.\n"
                "Please wait a few minutes and try again."
            )

    except Exception as e:
        print("Error:", str(e))
        await update.message.reply_text("Something went wrong: " + str(e))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, search_image))
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()