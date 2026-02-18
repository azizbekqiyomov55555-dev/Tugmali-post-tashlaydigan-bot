import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ================= CONFIG =================

TOKEN = "8312975127:AAFIXWrANgTpX_9ldK16OP97Tky3iRJqzL4"
CHANNEL = "@Azizbekl2026"
ADMIN_ID = 8537782289

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ================= STATE =================

class PostState(StatesGroup):
    waiting_button = State()
    waiting_link = State()
    waiting_time = State()

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
            [InlineKeyboardButton(
                text="📢 Kanalga kirish",
                url="https://t.me/Azizbekl2026"
            )]
        ])

        await message.answer(
            "❌ Botdan foydalanish uchun kanalga obuna bo‘ling!",
            reply_markup=kb
        )
        return

    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 Admin panel\n\n"
            "Post yuboring (matn yoki rasm + matn)"
        )
    else:
        await message.answer("✅ Bot ishlayapti")

# ================= ADMIN POST START =================

@dp.message(F.from_user.id == ADMIN_ID, StateFilter(None))
async def admin_post(message: Message, state: FSMContext):

    if message.text and message.text.startswith("/"):
        return

    await state.update_data(
        text=message.caption or message.text or "",
        photo=message.photo[-1].file_id if message.photo else None
    )

    await message.answer("🔘 Tugma nomini yuboring:")
    await state.set_state(PostState.waiting_button)

# ================= BUTTON =================

@dp.message(PostState.waiting_button, F.from_user.id == ADMIN_ID)
async def get_button(message: Message, state: FSMContext):

    await state.update_data(button=message.text)

    await message.answer("🔗 Tugma linkini yuboring:")
    await state.set_state(PostState.waiting_link)

# ================= LINK =================

@dp.message(PostState.waiting_link, F.from_user.id == ADMIN_ID)
async def get_link(message: Message, state: FSMContext):

    await state.update_data(link=message.text)

    await message.answer(
        "⏰ Post vaqtini yuboring\n\n"
        "Format:\nYYYY-MM-DD HH:MM\n\n"
        "Misol:\n2026-02-18 21:30"
    )

    await state.set_state(PostState.waiting_time)

# ================= TIME + SCHEDULE =================

@dp.message(PostState.waiting_time, F.from_user.id == ADMIN_ID)
async def schedule_post(message: Message, state: FSMContext):

    data = await state.get_data()

    try:
        post_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except:
        await message.answer("❌ Vaqt formati noto‘g‘ri!")
        return

    delay = (post_time - datetime.now()).total_seconds()

    if delay <= 0:
        await message.answer("❌ Vaqt kelajakda bo‘lishi kerak!")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=data["button"], url=data["link"])]
    ])

    await message.answer("👀 Preview:")

    if data["photo"]:
        await message.answer_photo(
            data["photo"],
            caption=data["text"],
            reply_markup=kb
        )
    else:
        await message.answer(
            data["text"],
            reply_markup=kb
        )

    await message.answer(f"✅ Post {message.text} da yuboriladi!")

    async def send_later():
        await asyncio.sleep(delay)

        if data["photo"]:
            await bot.send_photo(
                CHANNEL,
                data["photo"],
                caption=data["text"],
                reply_markup=kb
            )
        else:
            await bot.send_message(
                CHANNEL,
                data["text"],
                reply_markup=kb
            )

    asyncio.create_task(send_later())

    await state.clear()

# ================= RUN =================

async def main():
    print("🤖 Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
