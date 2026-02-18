import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = "8312975127:AAFIXWrANgTpX_9ldK16OP97Tky3iRJqzL4"
CHANNEL_ID = "@Azizbekl2026"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# START
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "📤 Kanalga post yuborish uchun:\n\n"
        "👉 Rasm + matn yuboring"
    )

# PHOTO POST
@dp.message(F.photo)
async def post_photo(message: Message):
    caption = message.caption or ""

    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=message.photo[-1].file_id,
        caption=caption
    )

    await message.answer("✅ Kanalga joylandi!")

# TEXT POST
@dp.message(F.text)
async def post_text(message: Message):
    if message.text.startswith("/"):
        return

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message.text
    )

    await message.answer("✅ Kanalga joylandi!")

# RUN
async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
