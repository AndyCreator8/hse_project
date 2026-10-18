
import os
from pathlib import Path
from uuid import uuid4
import asyncio
from model import analyze_photo
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PHOTO_DIR = Path("photos")
PHOTO_DIR.mkdir(exist_ok=True)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name

    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Я бот для оценки ауры фотографий.\n"
        "Отправь мне фотографию, и я её проанализирую!"
    )



async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Фотография получена!\n"
        "🔍 Анализируем ауру..."
    )

    picture = update.message.photo[-1]
    file = await picture.get_file()

    filename = PHOTO_DIR / f"{uuid4().hex}.jpg"
    await file.download_to_drive(filename)

    try:
        result = await asyncio.to_thread(analyze_photo, filename)

        await update.message.reply_text(
            f"✨ Результат анализа ауры: {round(result)}"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Не удалось проанализировать фотографию."
        )
        raise



if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в файле .env")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.PHOTO, photo))

app.run_polling()
