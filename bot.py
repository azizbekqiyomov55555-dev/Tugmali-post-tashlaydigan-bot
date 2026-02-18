import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = "8312975127:AAFIXWrANgTpX_9ldK16OP97Tky3iRJqzL4"
CHANNEL = "@Azizbekl2026"
ADMIN_ID = 8537782289  # admin id

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


# ================= SUB CHECK =================

async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ================= START =================

@dp.message(F.text == "/start")
async def start(message: Message):

    if not await check_sub(message.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga kirish", url=f"https://t.me/{CHANNEL[1:]}")]
        ])

        await message.answer(
            "❌ Botdan foydalanish uchun kanalga obuna bo‘ling!",
            reply_markup=kb
        )
        return

    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 Admin panel\n\n"
            "Post yuborish uchun:\n"
            "Matn + tugma yuboring\n\n"
            "Format:\n"
            "Text\n\nButton | link"
        )
    else:
        await message.answer("✅ Bot ishlayapti")


# ================= ADMIN POST =================

def parse_buttons(text):

    lines = text.split("\n")
    buttons = []

    clean_text = []

    for line in lines:
        if "|" in line:
            t, u = line.split("|", 1)
            buttons.append([InlineKeyboardButton(
                text=t.strip(),
                url=u.strip()
            )])
        else:
            clean_text.append(line)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

    return "\n".join(clean_text), kb


@dp.message(F.from_user.id == ADMIN_ID)
async def admin_post(message: Message):

    if message.text and message.text.startswith("/"):
        return

    text = message.caption or message.text or ""

    clean_text, kb = parse_buttons(text)

    # preview
    await message.answer("👀 Preview:")

    if message.photo:
        await message.answer_photo(
            photo=message.photo[-1].file_id,
            caption=clean_text,
            reply_markup=kb
        )
    else:
        await message.answer(
            clean_text,
            reply_markup=kb
        )

    # send to channel
    if message.photo:
        await bot.send_photo(
            CHANNEL,
            photo=message.photo[-1].file_id,
            caption=clean_text,
            reply_markup=kb
        )
    else:
        await bot.send_message(
            CHANNEL,
            clean_text,
            reply_markup=kb
        )

    await message.answer("✅ Kanalga joylandi!")


# ================= RUN =================

async def main():
    print("🤖 Super bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
