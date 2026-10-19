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
    filters,
)
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import CallbackQueryHandler

from sqlite_handler import DataBase

search_queue = []
active_battles = {}
user_to_battle = {}

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PHOTO_DIR = Path("photos")
PHOTO_DIR.mkdir(exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    user_id = update.effective_user.id
    exist = await db.get_user(str(user_id))
    if not exist:
        print(f"Создаю нового пользователя {name} - {user_id}")
        await db.new_user(str(user_id), name)
    # keyboard = [
    #         [
    #             InlineKeyboardButton("Поиск жертвы", callback_data="search_round"),
    #             InlineKeyboardButton("ХЗ", callback_data="reset_aura")
    #         ]
    #     ]
    #     # Оборачиваем кнопки в разметку
    # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Я бот для оценки ауры фотографий.\n"
        "Отправь мне фотографию, и я её проанализирую!"
    )


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("📸 Фотография получена!\n🔍 Анализируем ауру...")
    picture = update.message.photo[-1]
    file = await picture.get_file()
    filename = PHOTO_DIR / f"{uuid4().hex}.jpg"
    await file.download_to_drive(filename)
    try:
        result = await asyncio.to_thread(analyze_photo, filename)
        if user_id in user_to_battle:
            battle_id = user_to_battle[user_id]
            battle = active_battles[battle_id]
            # Записываем результат тому игроку, чей это id
            if battle["u1"] == user_id:
                battle["score1"] = result
                battle["ph1"] = filename
            else:
                battle["score2"] = result
                battle["ph2"] = filename

            # Проверяем, оба ли скинули фото
            if battle["score1"] is not None and battle["score2"] is not None:
                # ОБА СДАЛИ! Подводим итоги
                s1, s2 = battle["score1"], battle["score2"]

                if s1 > s2:
                    res1, res2 = "🏆 Вы победили!", "💀 Вы проиграли!"
                elif s2 > s1:
                    res1, res2 = "💀 Вы проиграли!", "🏆 Вы победили!"
                else:
                    res1, res2 = "🤝 Ничья!", "🤝 Ничья!"

                msg1 = f"Битва завершена!\nВаша аура: {s1}\nАура противника: {s2}\n\n{res1}"
                msg2 = f"Битва завершена!\nВаша аура: {s2}\nАура противника: {s1}\n\n{res2}"

                # Рассылаем результаты обоим
                await context.bot.send_message(battle["chat1"], msg1)
                await context.bot.send_message(battle["chat2"], msg2)
                await context.bot.send_photo(
                    battle["chat1"], battle["ph2"], caption="фото противника"
                )
                await context.bot.send_photo(
                    battle["chat2"], battle["ph1"], caption="фото противника"
                )
                # Очищаем батл из памяти
                del user_to_battle[battle["u1"]]
                del user_to_battle[battle["u2"]]
                del active_battles[battle_id]
            else:
                # Сдал только один, ждем второго
                await update.message.reply_text(
                    f"✨ Твоя аура: {result}. Ожидаем фото от противника..."
                )
    except Exception:
        await update.message.reply_text("❌ Не удалось проанализировать фотографию.")
        raise


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query.data)
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    await query.answer()

    if query.data == "search_round":
        print(search_queue)
        # Если пользователь уже в бою
        if user_id in user_to_battle:
            await query.edit_message_text("Вы уже находитесь в битве! Отправьте фото.")
            return

        if any(user_id == u_id for u_id, _ in search_queue):
            await query.edit_message_text("Вы уже в поиске... Ожидайте.")
            return

        if search_queue:
            opponent_id, opp_chat_id = search_queue.pop(0)

            battle_id = uuid4().hex
            active_battles[battle_id] = {
                "u1": opponent_id,
                "chat1": opp_chat_id,
                "score1": None,
                "u2": user_id,
                "chat2": chat_id,
                "score2": None,
            }

            user_to_battle[opponent_id] = battle_id
            user_to_battle[user_id] = battle_id
            await context.bot.send_message(
                opp_chat_id, "⚔️ Противник найден! Скорее отправляй фото!"
            )
            await query.edit_message_text("⚔️ Противник найден! Скорее отправляй фото!")
        else:
            # Если очередь пуста, встаем в нее
            search_queue.append((user_id, chat_id))
            await query.edit_message_text("🔍 Поиск противника... Ожидайте.")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем список с рядами кнопок
    keyboard = [
        [
            InlineKeyboardButton("Поиск жертвы", callback_data="search_round"),
            InlineKeyboardButton("ХЗ", callback_data="reset_aura"),
        ]
    ]
    # Оборачиваем кнопки в разметку
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Настройки пользователя. Выберите действие:", reply_markup=reply_markup
    )


if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в файле .env")


if __name__ == "__main__":
    db = DataBase("tgbot.db")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(db.connect())

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(CommandHandler("battle", settings))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
