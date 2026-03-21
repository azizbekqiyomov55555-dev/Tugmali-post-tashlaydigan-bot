import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
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

# ─── RANG PALITASI ────────────────────────────
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

# ─── FOYDALANUVCHI MA'LUMOTLARI ───────────────
user_data_store: dict = {}

def get_ud(uid):
    if uid not in user_data_store:
        user_data_store[uid] = {
            "matn": "",
            "rasm": None,
            "havola": "",
            "tugma_nomi": "",
            "rang": "yashil",
        }
    return user_data_store[uid]

# ─── KLAVIATURALAR ────────────────────────────
def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Yangi post yaratish", callback_data="yangi_post")],
    ])

def skip_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="skip")],
        [InlineKeyboardButton("❌ Bekor qilish",      callback_data="bekor")],
    ])

def rang_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Yashil",     callback_data="rang_yashil"),
            InlineKeyboardButton("🔴 Qizil",      callback_data="rang_qizil"),
            InlineKeyboardButton("🔵 Ko'k",       callback_data="rang_kok"),
        ],
        [
            InlineKeyboardButton("🟡 Sariq",      callback_data="rang_sariq"),
            InlineKeyboardButton("🟠 To'q sariq", callback_data="rang_toq_sariq"),
            InlineKeyboardButton("🟣 Binafsha",   callback_data="rang_binafsha"),
        ],
        [
            InlineKeyboardButton("⚫ Qora",       callback_data="rang_qora"),
            InlineKeyboardButton("⚪ Oq",         callback_data="rang_oq"),
            InlineKeyboardButton("🟤 Jigarrang",  callback_data="rang_jigarrang"),
        ],
        [InlineKeyboardButton("❌ Bekor qilish",   callback_data="bekor")],
    ])

def tasdiqlash_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Kanalga yuborish", callback_data="yuborish")],
        [InlineKeyboardButton("🔄 Qaytadan boshlash", callback_data="yangi_post")],
        [InlineKeyboardButton("❌ Bekor qilish",      callback_data="bekor")],
    ])

def post_tugma_kb(nomi, havola, rang_key):
    emoji = COLORS.get(rang_key, "🟢")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{emoji} {nomi}", url=havola)],
    ])

# ─── PREVIEW MATNI ────────────────────────────
def preview_text(ud):
    rang_emoji = COLORS.get(ud["rang"], "🟢")
    rang_nomi  = COLOR_NAMES.get(ud["rang"], "Yashil")
    return (
        "📋 <b>Post korinishi:</b>\n\n"
        f"📝 Matn: {ud['matn'] or '—'}\n"
        f"🖼 Rasm: {('✅ bor' if ud['rasm'] else '❌ yoq')}\n"
        f"🔗 Havola: {ud['havola'] or '—'}\n"
        f"🔘 Tugma nomi: {ud['tugma_nomi'] or '—'}\n"
        f"🎨 Rang: {rang_emoji} {rang_nomi}\n\n"
        "Yuborishni tasdiqlaysizmi?"
    )

# ─── /start ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xush kelibsiz!\n\n"
        "Bu bot orqali kanalga <b>rasmli, matnli, tugmali</b> post yuborasiz.",
        parse_mode="HTML",
        reply_markup=main_kb(),
    )
    return MAIN

# ─── YANGI POST BOSHLASH ──────────────────────
async def yangi_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        uid = query.from_user.id
    else:
        uid = update.message.from_user.id

    user_data_store[uid] = {
        "matn": "", "rasm": None,
        "havola": "", "tugma_nomi": "", "rang": "yashil",
    }

    msg = "✏️ <b>1-qadam:</b> Post matnini kiriting:"
    if query:
        await query.edit_message_text(msg, parse_mode="HTML",
                                      reply_markup=skip_kb())
    else:
        await update.message.reply_text(msg, parse_mode="HTML",
                                        reply_markup=skip_kb())
    return MATN_KIRISH

# ─── MATN QABUL ───────────────────────────────
async def matn_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    get_ud(uid)["matn"] = update.message.text
    await update.message.reply_text(
        "🖼 <b>2-qadam:</b> Rasm yuboring:",
        parse_mode="HTML",
        reply_markup=skip_kb(),
    )
    return RASM_KIRISH

# ─── RASM QABUL ───────────────────────────────
async def rasm_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    photo = update.message.photo[-1]
    get_ud(uid)["rasm"] = photo.file_id
    await update.message.reply_text(
        "🔗 <b>3-qadam:</b> Tugma havolasini kiriting:\n"
        "<i>Masalan: https://t.me/Azizbekl2026</i>",
        parse_mode="HTML",
        reply_markup=skip_kb(),
    )
    return HAVOLA_KIRISH

# ─── HAVOLA QABUL ─────────────────────────────
async def havola_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text.strip()
    if not text.startswith("http"):
        await update.message.reply_text(
            "⚠️ Havola http:// yoki https:// bilan boshlanishi kerak!\n"
            "Qaytadan kiriting:",
            reply_markup=skip_kb(),
        )
        return HAVOLA_KIRISH
    get_ud(uid)["havola"] = text
    await update.message.reply_text(
        "🔘 <b>4-qadam:</b> Tugma nomini kiriting:\n"
        "<i>Masalan: Buyurtma berish</i>",
        parse_mode="HTML",
        reply_markup=skip_kb(),
    )
    return TUGMA_NOMI_KIRISH

# ─── TUGMA NOMI QABUL ─────────────────────────
async def tugma_nomi_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    get_ud(uid)["tugma_nomi"] = update.message.text
    await update.message.reply_text(
        "🎨 <b>5-qadam:</b> Tugma rangini tanlang:",
        parse_mode="HTML",
        reply_markup=rang_kb(),
    )
    return RANG_TANLA

# ─── RANG TANLASH ─────────────────────────────
async def rang_tanlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid  = query.from_user.id
    rang = query.data[5:]  # "rang_yashil" → "yashil"
    get_ud(uid)["rang"] = rang
    emoji = COLORS.get(rang, "🟢")
    name  = COLOR_NAMES.get(rang, rang)

    ud = get_ud(uid)
    await query.edit_message_text(
        f"✅ Rang: {emoji} {name}\n\n" + preview_text(ud),
        parse_mode="HTML",
        reply_markup=tasdiqlash_kb(),
    )
    return TASDIQLASH

# ─── SKIP ─────────────────────────────────────
async def skip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    ud  = get_ud(uid)

    # Qaysi holatda skip bosildi — keyingiga o'tamiz
    # Matn → Rasm
    if ud["matn"] == "" and ud["rasm"] is None and ud["havola"] == "":
        await query.edit_message_text(
            "🖼 <b>2-qadam:</b> Rasm yuboring:",
            parse_mode="HTML", reply_markup=skip_kb(),
        )
        return RASM_KIRISH
    # Rasm → Havola
    elif ud["rasm"] is None and ud["havola"] == "":
        await query.edit_message_text(
            "🔗 <b>3-qadam:</b> Tugma havolasini kiriting:\n"
            "<i>Masalan: https://t.me/Azizbekl2026</i>",
            parse_mode="HTML", reply_markup=skip_kb(),
        )
        return HAVOLA_KIRISH
    # Havola → Tugma nomi
    elif ud["havola"] == "" and ud["tugma_nomi"] == "":
        await query.edit_message_text(
            "🔘 <b>4-qadam:</b> Tugma nomini kiriting:",
            parse_mode="HTML", reply_markup=skip_kb(),
        )
        return TUGMA_NOMI_KIRISH
    # Tugma nomi → Rang
    else:
        await query.edit_message_text(
            "🎨 <b>5-qadam:</b> Tugma rangini tanlang:",
            parse_mode="HTML", reply_markup=rang_kb(),
        )
        return RANG_TANLA

# ─── KANALGA YUBORISH ─────────────────────────
async def kanalga_yuborish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    ud  = get_ud(uid)

    tugma_kb = None
    if ud["havola"] and ud["tugma_nomi"]:
        tugma_kb = post_tugma_kb(ud["tugma_nomi"], ud["havola"], ud["rang"])

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
                text=ud["matn"] or "📢 Yangi post!",
                reply_markup=tugma_kb,
            )

        rang_emoji = COLORS.get(ud["rang"], "🟢")
        rang_nomi  = COLOR_NAMES.get(ud["rang"], "Yashil")
        await query.edit_message_text(
            f"✅ Post kanalga muvaffaqiyatli yuborildi!\n"
            f"🎨 Tugma rangi: {rang_emoji} {rang_nomi}",
            reply_markup=main_kb(),
        )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Xatolik: {str(e)}\n\n"
            f"Bot kanalda admin ekanligini tekshiring!",
            reply_markup=main_kb(),
        )

    user_data_store.pop(uid, None)
    return MAIN

# ─── BEKOR QILISH ─────────────────────────────
async def bekor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    user_data_store.pop(uid, None)
    await query.edit_message_text(
        "❌ Bekor qilindi.\n\nYangi post yaratish uchun tugmani bosing:",
        reply_markup=main_kb(),
    )
    return MAIN

# ─── MAIN ─────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(yangi_post, pattern="^yangi_post$"),
        ],
        states={
            MAIN: [
                CallbackQueryHandler(yangi_post, pattern="^yangi_post$"),
            ],
            MATN_KIRISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, matn_qabul),
                CallbackQueryHandler(skip_handler, pattern="^skip$"),
                CallbackQueryHandler(bekor, pattern="^bekor$"),
            ],
            RASM_KIRISH: [
                MessageHandler(filters.PHOTO, rasm_qabul),
                CallbackQueryHandler(skip_handler, pattern="^skip$"),
                CallbackQueryHandler(bekor, pattern="^bekor$"),
            ],
            HAVOLA_KIRISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, havola_qabul),
                CallbackQueryHandler(skip_handler, pattern="^skip$"),
                CallbackQueryHandler(bekor, pattern="^bekor$"),
            ],
            TUGMA_NOMI_KIRISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, tugma_nomi_qabul),
                CallbackQueryHandler(skip_handler, pattern="^skip$"),
                CallbackQueryHandler(bekor, pattern="^bekor$"),
            ],
            RANG_TANLA: [
                CallbackQueryHandler(rang_tanlash, pattern="^rang_"),
                CallbackQueryHandler(bekor, pattern="^bekor$"),
            ],
            TASDIQLASH: [
                CallbackQueryHandler(kanalga_yuborish, pattern="^yuborish$"),
                CallbackQueryHandler(yangi_post, pattern="^yangi_post$"),
                CallbackQueryHandler(bekor, pattern="^bekor$"),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(bekor, pattern="^bekor$"),
        ],
    )

    app.add_handler(conv)
    logger.info("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
