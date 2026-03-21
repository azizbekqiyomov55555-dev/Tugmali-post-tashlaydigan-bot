import logging
import configparser
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ───────────────────────────────────────────────
#  CONFIG YUKLAB OLISH
# ───────────────────────────────────────────────
config = configparser.RawConfigParser()

def load_config():
    with open("config.txt", "r", encoding="utf-8") as f:
        content = "[main]\n" + f.read()
    config.read_string(content)

load_config()

BOT_TOKEN     = config.get("main", "BOT_TOKEN")
CHANNEL_ID    = config.get("main", "CHANNEL_ID")
STICKER_ID    = config.get("main", "STICKER_ID")
POST_TEXT     = config.get("main", "POST_TEXT").replace("\\n", "\n")
POLL_QUESTION = config.get("main", "POLL_QUESTION")
POLL_OPTIONS  = config.get("main", "POLL_OPTIONS").split(",")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────
#  RANG PALITASI
# ───────────────────────────────────────────────
COLORS = {
    "yashil":     "🟢",
    "qizil":      "🔴",
    "kok":        "🔵",
    "sariq":      "🟡",
    "toq_sariq":  "🟠",
    "binafsha":   "🟣",
    "qora":       "⚫",
    "oq":         "⚪",
    "jigarrang":  "🟤",
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

user_color: dict = {}

def get_emoji(user_id):
    return COLORS.get(user_color.get(user_id, "yashil"), "🟢")

def get_name(user_id):
    return COLOR_NAMES.get(user_color.get(user_id, "yashil"), "Yashil")

# ───────────────────────────────────────────────
#  TUGMALAR
# ───────────────────────────────────────────────
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🟢 Buyurtma berish",      callback_data="buyurtma")],
        [InlineKeyboardButton("🎨 Tugma rangini tanlash", callback_data="rang_tanla")],
        [InlineKeyboardButton("⬅️ Orqaga",               callback_data="orqaga")],
    ]
    return InlineKeyboardMarkup(keyboard)

def order_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga post",         callback_data="kanal_post")],
        [InlineKeyboardButton("📊 So'rovnoma yuborish",  callback_data="sorovnoma")],
        [InlineKeyboardButton("🎭 Stiker yuborish",      callback_data="stiker")],
        [InlineKeyboardButton("⬅️ Orqaga",               callback_data="orqaga")],
    ]
    return InlineKeyboardMarkup(keyboard)

def color_keyboard():
    keyboard = [
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
        [InlineKeyboardButton("⬅️ Orqaga",        callback_data="orqaga")],
    ]
    return InlineKeyboardMarkup(keyboard)

def post_keyboard(user_id):
    emoji = get_emoji(user_id)
    name  = get_name(user_id)
    keyboard = [
        [InlineKeyboardButton(f"{emoji} Buyurtma berish", callback_data="buyurtma")],
        [InlineKeyboardButton("⬅️ Orqaga",                callback_data="orqaga")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ───────────────────────────────────────────────
#  /start
# ───────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xush kelibsiz!\n\nQuyidagi tugmalardan birini tanlang:",
        reply_markup=main_keyboard(),
    )

# ───────────────────────────────────────────────
#  CALLBACK HANDLER
# ───────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid  = query.from_user.id

    if data == "buyurtma":
        await query.edit_message_text(
            "🛒 Buyurtma bo'limi\n\nNimani amalga oshirmoqchisiz?",
            reply_markup=order_keyboard(),
        )

    elif data == "rang_tanla":
        emoji = get_emoji(uid)
        name  = get_name(uid)
        await query.edit_message_text(
            f"🎨 Hozirgi rang: {emoji} {name}\n\nYangi rang tanlang:",
            reply_markup=color_keyboard(),
        )

    elif data.startswith("rang_"):
        rang = data[5:]
        user_color[uid] = rang
        emoji = COLORS.get(rang, "🟢")
        name  = COLOR_NAMES.get(rang, rang)
        await query.edit_message_text(
            f"✅ Tugma rangi {emoji} {name} ga o'zgartirildi!\n\n"
            f"Kanalga post yuborganingizda tugma shu rangda bo'ladi.",
            reply_markup=main_keyboard(),
        )

    elif data == "kanal_post":
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=POST_TEXT,
            reply_markup=post_keyboard(uid),
        )
        emoji = get_emoji(uid)
        name  = get_name(uid)
        await query.edit_message_text(
            f"✅ Post {emoji} {name} rangli tugma bilan kanalga yuborildi!",
            reply_markup=order_keyboard(),
        )

    elif data == "sorovnoma":
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question=POLL_QUESTION,
            options=POLL_OPTIONS,
            is_anonymous=True,
            allows_multiple_answers=False,
        )
        await query.edit_message_text(
            "✅ So'rovnoma kanalga yuborildi!",
            reply_markup=order_keyboard(),
        )

    elif data == "stiker":
        await context.bot.send_sticker(
            chat_id=CHANNEL_ID,
            sticker=STICKER_ID,
        )
        await query.edit_message_text(
            "✅ Stiker kanalga yuborildi!",
            reply_markup=order_keyboard(),
        )

    elif data == "orqaga":
        await query.edit_message_text(
            "👋 Xush kelibsiz!\n\nQuyidagi tugmalardan birini tanlang:",
            reply_markup=main_keyboard(),
        )

# ───────────────────────────────────────────────
#  MAIN
# ───────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
