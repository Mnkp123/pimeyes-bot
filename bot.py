import requests
import base64
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8953302856:AAH0mMmoJt1fTBjfJ-Z2_PbbtTbQ3VgO2Xw")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start command received!")
    await update.message.reply_text(
        "Welcome to PimEyes Face Search Bot!\n\n"
        "Send me any face image and I will search it on PimEyes automatically.\n\n"
        "Send an image to get started!"
    )

async def search_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Image received from user!")
    await update.message.reply_text("Image received! Searching on PimEyes...")
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        print("Image downloaded successfully!")
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data = "data:image/jpeg;base64," + base64_image
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
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
            if faces:
                face_id = faces[0]["id"]
                await update.message.reply_text(
                    "Face detected successfully!\n\n"
                    "Face ID: " + face_id + "\n\n"
                    "View Results:\n"
                    "https://pimeyes.com/en/results/" + face_id
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