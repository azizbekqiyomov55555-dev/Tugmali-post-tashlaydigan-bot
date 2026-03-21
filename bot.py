import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ─── SOZLAMALAR ───────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── HOLATLAR ─────────────────────────────────
(
    MAIN,
    MATN_KIRISH,
    RASM_KIRISH,
    HAVOLA_KIRISH,
    TUGMA_NOMI_KIRISH,
    RANG_TANLA,
    TASDIQLASH,
) = range(7)

# ─── RANGLAR (inline post tugmasi uchun emoji) ─
COLORS = {
    "yashil":    "🟢",
    "qizil":     "🔴",
    "kok":       "🔵",
    "sariq":     "🟡",
    "toq_sariq": "🟠",
    "binafsha":  "🟣",
    "qora":      "⚫",
    "oq":        "⚪",
    "jigarrang": "🟤",
}
COLOR_NAMES = {
    "yashil":    "Yashil",
    "qizil":     "Qizil",
    "kok":       "Ko'k",
    "sariq":     "Sariq",
    "toq_sariq": "To'q sariq",
    "binafsha":  "Binafsha",
    "qora":      "Qora",
    "oq":        "Oq",
    "jigarrang": "Jigarrang",
}

user_data_store: dict = {}

def get_ud(uid):
    if uid not in user_data_store:
        user_data_store[uid] = {
            "matn": "", "rasm": None,
            "havola": "", "tugma_nomi": "", "rang": "yashil",
        }
    return user_data_store[uid]

# ─── REPLY KEYBOARD (RANGLI TUGMALAR) ─────────
def main_reply_kb():
    """Asosiy menyu — yashil va qizil tugmalar"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🟢 Yangi post yaratish")],
            [KeyboardButton("❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

def post_jarayoni_kb():
    """Post jarayonida — otkazib yuborish va bekor qilish"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("⏭ O'tkazib yuborish")],
            [KeyboardButton("❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

def tasdiqlash_reply_kb():
    """Tasdiqlash — yashil yuborish, qizil bekor"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("✅ Kanalga yuborish")],
            [KeyboardButton("🔄 Qaytadan boshlash")],
            [KeyboardButton("❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def rang_reply_kb():
    """Rang tanlash klaviaturasi"""
    return ReplyKeyboardMarkup(
        [
            ["🟢 Yashil",     "🔴 Qizil",      "🔵 Ko'k"],
            ["🟡 Sariq",      "🟠 To'q sariq", "🟣 Binafsha"],
            ["⚫ Qora",       "⚪ Oq",         "🟤 Jigarrang"],
            ["❌ Bekor qilish"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# ─── INLINE (kanalga yuboriladigan post tugmasi) ─
def post_inline_kb(nomi, havola, rang_key):
    emoji = COLORS.get(rang_key, "🟢")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{emoji} {nomi}", url=havola)],
    ])

# ─── RANG MATNIDAN KEY OLISH ──────────────────
RANG_MAP = {
    "🟢 Yashil":     "yashil",
    "🔴 Qizil":      "qizil",
    "🔵 Ko'k":       "kok",
    "🟡 Sariq":      "sariq",
    "🟠 To'q sariq": "toq_sariq",
    "🟣 Binafsha":   "binafsha",
    "⚫ Qora":       "qora",
    "⚪ Oq":         "oq",
    "🟤 Jigarrang":  "jigarrang",
}

# ─── PREVIEW ─────────────────────────────────
def preview_text(ud):
    rang_key  = ud.get("rang", "yashil")
    rang_emoji = COLORS.get(rang_key, "🟢")
    rang_nomi  = COLOR_NAMES.get(rang_key, "Yashil")
    rasm_status = "✅ bor" if ud["rasm"] else "yoq"
    return (
        "<b>Post korinishi:</b>\n\n"
        f"Matn: {ud['matn'] or '—'}\n"
        f"Rasm: {rasm_status}\n"
        f"Havola: {ud['havola'] or '—'}\n"
        f"Tugma nomi: {ud['tugma_nomi'] or '—'}\n"
        f"Tugma rangi: {rang_emoji} {rang_nomi}\n\n"
        "Yuborishni tasdiqlaysizmi?"
    )

# ─── /start ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xush kelibsiz!\n\nKanalga post yuborish uchun quyidagi tugmani bosing:",
        reply_markup=main_reply_kb(),
    )
    return MAIN

# ─── YANGI POST ───────────────────────────────
async def yangi_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    user_data_store[uid] = {
        "matn": "", "rasm": None,
        "havola": "", "tugma_nomi": "", "rang": "yashil",
    }
    await update.message.reply_text(
        "1-qadam: Post matnini kiriting:",
        reply_markup=post_jarayoni_kb(),
    )
    return MATN_KIRISH

# ─── MATN ─────────────────────────────────────
async def matn_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.message.from_user.id
    text = update.message.text
    if text == "⏭ O'tkazib yuborish":
        get_ud(uid)["matn"] = ""
    elif text == "❌ Bekor qilish":
        return await bekor(update, context)
    else:
        get_ud(uid)["matn"] = text

    await update.message.reply_text(
        "2-qadam: Rasm yuboring:",
        reply_markup=post_jarayoni_kb(),
    )
    return RASM_KIRISH

# ─── RASM ─────────────────────────────────────
async def rasm_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if update.message.photo:
        get_ud(uid)["rasm"] = update.message.photo[-1].file_id
    await update.message.reply_text(
        "3-qadam: Tugma havolasini kiriting:\nMasalan: https://t.me/Azizbekl2026",
        reply_markup=post_jarayoni_kb(),
    )
    return HAVOLA_KIRISH

async def rasm_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.message.from_user.id
    text = update.message.text
    if text == "❌ Bekor qilish":
        return await bekor(update, context)
    await update.message.reply_text(
        "3-qadam: Tugma havolasini kiriting:\nMasalan: https://t.me/Azizbekl2026",
        reply_markup=post_jarayoni_kb(),
    )
    return HAVOLA_KIRISH

# ─── HAVOLA ───────────────────────────────────
async def havola_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.message.from_user.id
    text = update.message.text
    if text == "❌ Bekor qilish":
        return await bekor(update, context)
    if text == "⏭ O'tkazib yuborish":
        get_ud(uid)["havola"] = ""
    else:
        if not text.startswith("http"):
            await update.message.reply_text(
                "Havola https:// bilan boshlanishi kerak! Qayta kiriting:",
                reply_markup=post_jarayoni_kb(),
            )
            return HAVOLA_KIRISH
        get_ud(uid)["havola"] = text

    await update.message.reply_text(
        "4-qadam: Tugma nomini kiriting:\nMasalan: Buyurtma berish",
        reply_markup=post_jarayoni_kb(),
    )
    return TUGMA_NOMI_KIRISH

# ─── TUGMA NOMI ───────────────────────────────
async def tugma_nomi_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.message.from_user.id
    text = update.message.text
    if text == "❌ Bekor qilish":
        return await bekor(update, context)
    if text != "⏭ O'tkazib yuborish":
        get_ud(uid)["tugma_nomi"] = text

    await update.message.reply_text(
        "5-qadam: Tugma rangini tanlang:",
        reply_markup=rang_reply_kb(),
    )
    return RANG_TANLA

# ─── RANG ─────────────────────────────────────
async def rang_tanlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.message.from_user.id
    text = update.message.text
    if text == "❌ Bekor qilish":
        return await bekor(update, context)

    rang_key = RANG_MAP.get(text, "yashil")
    get_ud(uid)["rang"] = rang_key

    ud = get_ud(uid)
    await update.message.reply_text(
        preview_text(ud),
        parse_mode="HTML",
        reply_markup=tasdiqlash_reply_kb(),
    )
    return TASDIQLASH

# ─── KANALGA YUBORISH ─────────────────────────
async def kanalga_yuborish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.message.from_user.id
    text = update.message.text
    ud   = get_ud(uid)

    if text == "🔄 Qaytadan boshlash":
        return await yangi_post(update, context)
    if text == "❌ Bekor qilish":
        return await bekor(update, context)

    tugma_kb = None
    if ud["havola"] and ud["tugma_nomi"]:
        tugma_kb = post_inline_kb(ud["tugma_nomi"], ud["havola"], ud["rang"])

    try:
        if ud["rasm"]:
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=ud["rasm"],
                caption=ud["matn"] or None,
                reply_markup=tugma_kb,
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=ud["matn"] or "Yangi post!",
                reply_markup=tugma_kb,
            )

        rang_emoji = COLORS.get(ud["rang"], "🟢")
        rang_nomi  = COLOR_NAMES.get(ud["rang"], "Yashil")
        await update.message.reply_text(
            f"Post kanalga yuborildi! {rang_emoji} {rang_nomi} rangli tugma bilan.",
            reply_markup=main_reply_kb(),
        )
    except Exception as e:
        await update.message.reply_text(
            f"Xatolik: {str(e)}\n\nBot kanalda admin ekanligini tekshiring!",
            reply_markup=main_reply_kb(),
        )

    user_data_store.pop(uid, None)
    return MAIN

# ─── BEKOR ────────────────────────────────────
async def bekor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    user_data_store.pop(uid, None)
    await update.message.reply_text(
        "Bekor qilindi. Yangi post yaratish uchun tugmani bosing.",
        reply_markup=main_reply_kb(),
    )
    return MAIN

# ─── MAIN ─────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^🟢 Yangi post yaratish$"), yangi_post),
        ],
        states={
            MAIN: [
                MessageHandler(filters.Regex("^🟢 Yangi post yaratish$"), yangi_post),
            ],
            MATN_KIRISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, matn_qabul),
            ],
            RASM_KIRISH: [
                MessageHandler(filters.PHOTO, rasm_qabul),
                MessageHandler(filters.TEXT & ~filters.COMMAND, rasm_skip),
            ],
            HAVOLA_KIRISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, havola_qabul),
            ],
            TUGMA_NOMI_KIRISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, tugma_nomi_qabul),
            ],
            RANG_TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, rang_tanlash),
            ],
            TASDIQLASH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, kanalga_yuborish),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^❌ Bekor qilish$"), bekor),
        ],
    )

    app.add_handler(conv)
    logger.info("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
