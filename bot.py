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
    KeyboardButton,
)
from telegram.ext import CallbackQueryHandler

from sqlite_handler import DataBase
from collections import OrderedDict

search_queue = OrderedDict()
active_battles = {}
user_to_battle = {}

main_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("Поиск игроков"), KeyboardButton("Счётчик ауры")]],
    resize_keyboard=True,
    is_persistent=True,
)

cancel_button = KeyboardButton("Отмена")

play_again_button = KeyboardButton("Сыграть еще раз")

back_to_menu_button = KeyboardButton("Главное меню")


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PHOTO_DIR = Path("photos")
PHOTO_DIR.mkdir(exist_ok=True)
PHOTO = object()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    user_id = update.effective_user.id
    exist = await db.get_user(str(user_id))
    if not exist:
        print(f"Создаю нового пользователя {name} - {user_id}")
        await db.new_user(str(user_id), name)
    # await update.message.reply_text(
    #     """Скинь фотку на оценку ауры или нажми на кнопку\n[Поиск игроков], чтобы сразиться с другими игроками""",
    #     reply_markup=main_keyboard,
    # )
    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Я бот для оценки ауры фотографий.\n"
        "Скинь фотку на оценку ауры или нажми на кнопку\n[Поиск игроков], чтобы сразиться с другими игроками",
        reply_markup=main_keyboard,
    )


async def check_if_user_sent_photo(user_id):
    battle = active_battles[user_to_battle[user_id]]
    if battle["u1"] == user_id:
        return battle["score1"], battle["score2"]
    else:
        return battle["score2"], battle["score1"]

async def get_photo(picture):
    file = await picture.get_file()
    await file.download_to_drive(filename)
    filename = PHOTO_DIR / f"{uuid4().hex}.jpg"
    result = await asyncio.to_thread(analyze_photo, filename)
    if result >= 5000:
        reaction = "💀🥶💀"
    elif 0 < result < 5000:
        reaction = "😎"
    elif -5000 < result <= 0:
        reaction = "😒"
    else:
        reaction = "💩💩💩"
    return result, reaction, filename

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = db.get_user_state(user_id)
    if state in (0, 3):
        if state == 3:
            _in_battle = check_if_user_sent_photo(user_id)
            if _in_battle == (None, None):
                picture = update.message.photo[-2]
                try:
                    result, reaction, filename = await get_photo(picture)
                except Exception as ex:
                    print(ex)
                    await update.message.reply_text("❌ Не удалось проанализировать фотографию. Отправь еще раз")
                    return
                await update.message.reply_text("📸 Фотография получена!\n Ждём фотки противника...")
                battle_id = user_to_battle[user_id]
                battle = active_battles[battle_id]
                if battle["u1"] == user_id:
                    battle["score1"] = result
                    battle["ph1"] = filename
                else:
                    battle["score2"] = result
                    battle["ph2"] = filename
            elif battle["score1"] is not None and battle["score2"] is not None:





                
        else:
            await update.message.reply_text("📸 Фотография получена!\n🔍 Анализируем ауру...")
            picture = update.message.photo[-2]
            result, reaction, _ = await get_photo(picture)
            await update.message.reply_text(
                    f"Твоя аура: {result} {reaction}."
                )
    
    
    try:
        
        if user_id in user_to_battle:
            battle_id = user_to_battle[user_id]
            battle = active_battles[battle_id]

            if battle["u1"] == user_id:
                battle["score1"] = result
                battle["ph1"] = filename
            else:
                battle["score2"] = result
                battle["ph2"] = filename

            if battle["score1"] is not None and battle["score2"] is not None:
                s1, s2 = battle["score1"], battle["score2"]

                if s1 > s2:
                    res1, res2 = "🏆 Вы победили!", "💀 Вы проиграли!"
                elif s2 > s1:
                    res1, res2 = "💀 Вы проиграли!", "🏆 Вы победили!"
                else:
                    res1, res2 = "🤝 Ничья!", "🤝 Ничья!"

                msg1 = f"Битва завершена!\nВаша аура: {s1}\nАура противника: {s2}\n\n{res1}"
                msg2 = f"Битва завершена!\nВаша аура: {s2}\nАура противника: {s1}\n\n{res2}"

                await context.bot.send_message(battle["chat1"], msg1)
                await context.bot.send_message(battle["chat2"], msg2)
                await context.bot.send_photo(
                    battle["chat1"],
                    battle["ph2"],
                    caption="фото противника",
                    reply_markup=ReplyKeyboardMarkup(
                        [[play_again_button, back_to_menu_button]], resize_keyboard=True
                    ), 
                )
                await context.bot.send_photo(
                    battle["chat2"],
                    battle["ph1"],
                    caption="фото противника",
                    reply_markup=ReplyKeyboardMarkup(
                        [[play_again_button, back_to_menu_button]], resize_keyboard=True
                    ), 
                )
                await db.set_score(battle["u1"], battle["score1"])
                await db.set_score(battle["u2"], battle["score2"])
                await db.set_user_status(battle["u1"], 0)
                await db.set_user_status(battle["u2"], 0)

                del user_to_battle[battle["u1"]]
                del user_to_battle[battle["u2"]]
                del active_battles[battle_id]
            else:
                
                await update.message.reply_text(
                    f"Твоя аура: {result} {reaction}. Ожидаем фото от противника..."
                )
        else:
            await update.message.reply_text(f"Твоя аура: {result} {reaction}.")
            await db.set_score(user_id, result)
    except Exception:
        await update.message.reply_text("❌ Не удалось проанализировать фотографию.")
        raise


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    print(text)
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    if text in ("Поиск игроков", "Сыграть еще раз"):
        state = await db.get_user_state(user_id)

        if state[0] == 2:
            await update.message.reply_text(
                "⚔️ Вы уже находитесь в битве! Отправьте фото.", reply_markup=cancel_button
            )
            return

        if state[0] == 1:
            await update.message.reply_text(
                "⌛ Ты уже в поиске... Жди соперника.", reply_markup=cancel_button
            )
            return

        if search_queue:
            opponent_id, opp_chat_id = search_queue.popitem(last=False)
            await db.set_user_status(user_id, 2)
            await db.set_user_status(opponent_id, 2)
            battle_id = uuid4().hex
            active_battles[battle_id] = {
                "u1": opponent_id,
                "chat1": opp_chat_id,
                "score1": None,
                "u2": user_id,
                "chat2": chat_id,
                "score2": None,
            }
            user_chat = await context.bot.get_chat(user_id)
            opp_chat = await context.bot.get_chat(opponent_id)

            user_to_battle[opponent_id] = battle_id
            user_to_battle[user_id] = battle_id
            await context.bot.send_message(
                opp_chat_id,
                f"⚔️ Противник {user_chat.first_name} aka @{user_chat.username} найден! Скорее отправляй фото!",
                reply_markup=ReplyKeyboardMarkup([[cancel_button]], resize_keyboard=True),
            )
            await update.message.reply_text(
                f"⚔️ Противник {opp_chat.first_name} aka @{opp_chat.username} найден! Скорее отправляй фото!",
                reply_markup=ReplyKeyboardMarkup([[cancel_button]], resize_keyboard=True)
            )
        else:
            await db.set_user_status(user_id, 1)
            search_queue[user_id] = chat_id
            await update.message.reply_text(
                "⌛ Поиск противника... Ожидайте.",
                reply_markup=ReplyKeyboardMarkup([[cancel_button]], resize_keyboard=True,
                    )
            )
    if text == "Отмена":
        state = await db.get_user_state(user_id)
        print(state)
        if state[0] == 1:
            await update.message.reply_text("❌ Поиск отменен", reply_markup=main_keyboard)
            del search_queue[user_id]
        elif state[0] == 2:
            battle_id = user_to_battle.pop(user_id)
            current_battle = active_battles[battle_id]
            opponent_chat_id = (
                current_battle["chat1"]
                if current_battle["chat1"] != user_id
                else current_battle["chat2"]
            )
            opp_id = (
                current_battle["u1"]
                if current_battle["u1"] != user_id
                else current_battle["u2"]
            )
            await db.set_user_status(opp_id, 0)
            await update.message.reply_text("❌ Матч отменен", reply_markup=main_keyboard)
            await context.bot.send_message(
                opponent_chat_id, "❌ Противник отменил матч", reply_markup=main_keyboard
            )
            del current_battle
            del user_to_battle[opp_id]
        else:
            await update.message.reply_text(
                """Скинь фотку на оценку ауры или нажми на кнопку\n[Поиск игроков], чтобы сразиться с другими игроками""",
                reply_markup=main_keyboard,
            )
        await db.set_user_status(user_id, 0)
    if text == "Главное меню":
        state = await db.get_user_state(user_id)
        if state[0] == 0:
            await update.message.reply_text(
                """Скинь фотку на оценку ауры или нажми на кнопку\n[Поиск игроков], чтобы сразиться с другими игроками""",
                reply_markup=main_keyboard,
            )
    if text == "Счётчик ауры":
        print("a")
        state = await db.get_user_state(user_id)
        if state[0] == 0:

            score = await db.get_user_score(user_id)
            if score:
                await update.message.reply_text(f"Твоя итоговая аура: {score[0]}")

if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в файле .env")

async def post_init():
    await db.connect()
    await db.update_users()

async def post_shutdown():
    await db.close()

if __name__ == "__main__":
    db = DataBase("tgbot.db")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .concurrent_updates(True)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    app.run_polling()
 