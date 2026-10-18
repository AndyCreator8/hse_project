import asyncio
import logging
import os 
from aiogram import Bot, Dispatcher, F 
from aiogram.types import Message 
from aiogram.filters import Command
from PIL import Image
from LM import LearningMachine, val_tfms
BOT_TOKEN = open("TOKEN").readline()
SAVE_DIR = "photos_folder"


dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Кинь фото с максиальной аурой")


@dp.message(F.photo)
async def handle_photo(message: Message, bot): # Aiogram возвращает массив фото разных размеров. [-1] — самое высокое качество.
    photo_data = message.photo[-1]
    file_name = f"{message.from_user.id}_{message.photo[-1].file_id}.jpg"
    try:
        print("message")
        await bot.download(photo_data, destination=f"junk/{file_name}")
        Lm = LearningMachine("mps", False, val_trsf=val_tfms, path="last_model.pt")
        x = Lm.predict(f"junk/{file_name}")
        print(x)
        maxarg = max(x)
        if x.index(maxarg) == 1:
            maxarg *= -1
        maxarg *= 1000
        await message.answer(f"AURA {maxarg}")
    except Exception as ex:
        print(f"Не удалось обработать {ex}")

async def main():
    os.makedirs(SAVE_DIR, exist_ok=True)
    bot = Bot(token=BOT_TOKEN)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())