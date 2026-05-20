import requests
import base64
import random
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

def get_anti_detection_headers():
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
        "Sec-Fetch-Site": "same-origin"
    }

def get_ai_summary(face_count, face_id):
    search_url = f"https://pimeyes.com/en/results/{face_id}"
    if face_count == 1:
        summary = (
            "AI Analysis: One face was successfully detected in your image. "
            "PimEyes has processed the facial features and generated a unique face signature. "
            f"The search is now complete. Visit the results link to see where this face appears online."
        )
    else:
        summary = (
            f"AI Analysis: {face_count} faces were detected in your image. "
            "PimEyes processed all detected faces and generated unique signatures for each. "
            "The primary face has been used for the search query."
        )
    return summary

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start command received!")
    await update.message.reply_text(
        "Welcome to PimEyes Face Search Bot!\n\n"
        "Features:\n"
        "- Automated face search on PimEyes\n"
        "- Anti-detection headers rotation\n"
        "- AI-assisted result analysis\n\n"
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

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data = "data:image/jpeg;base64," + base64_image

        headers = get_anti_detection_headers()
        print("Using User-Agent:", headers["User-Agent"])

        payload = {"image": image_data}
        print("Sending to PimEyes API...")

        response = requests.post(
            "https://pimeyes.com/api/upload/file",
            json=payload,
            headers=headers
        )
        print("PimEyes response:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            faces = data.get("faces", [])
            face_count = len(faces)

            if faces:
                face_id = faces[0]["id"]
                ai_summary = get_ai_summary(face_count, face_id)
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
            await update.message.reply_text("Error: " + str(response.status_code))

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