import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = ("8158005825:AAFKlFXvqdVQUfkA6NVtmNTMGC4rSGIc778")  # Railway uchun
ADMIN_ID = 8332077004  # admin id
CHANNEL = "@Azizbekl2026"  # kanal username

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ====== POST COMMAND ======
@dp.message(Command("post"))
async def send_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    bot_username = (await bot.me()).username

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 Botga kiring",
                    url=f"https://t.me/{bot_username}"
                )
            ]
        ]
    )

    await bot.send_message(
        chat_id=CHANNEL,
        text="🚀 Botdan foydalanish uchun pastdagi tugmani bosing:",
        reply_markup=keyboard
    )

    await message.answer("✅ Post kanalga yuborildi!")


# ====== START ======
async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
