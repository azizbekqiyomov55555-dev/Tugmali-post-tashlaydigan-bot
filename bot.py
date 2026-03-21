import logging
import os
import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─── SOZLAMALAR ───────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")

# webapp.html ni hosting qilingan URL — Railway yoki GitHub Pages
WEBAPP_URL = os.getenv("https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/", "https://YOUR_GITHUB_USERNAME.github.io/YOUR_REPO/webapp.html")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── RANGLAR ──────────────────────────────────
RANG_COLORS = {
    "yashil":    "#4CAF50",
    "qizil":     "#e53935",
    "kok":       "#1E88E5",
    "sariq":     "#FDD835",
    "toq_sariq": "#FB8C00",
    "binafsha":  "#8E24AA",
    "qora":      "#212121",
    "oq":        "#eeeeee",
    "jigarrang": "#6D4C41",
}
RANG_EMOJI = {
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

# ─── ASOSIY MENYU ─────────────────────────────
def main_kb():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(
            "📝 Post yaratish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]],
        resize_keyboard=True,
    )

# ─── /start ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xush kelibsiz!\n\n"
        "Quyidagi tugmani bosing va post yarating:",
        reply_markup=main_kb(),
    )

# ─── WEBAPP DAN KELGAN MA'LUMOT ───────────────
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        await update.message.reply_text("Xatolik: ma'lumot noto'g'ri formatda.")
        return

    matn       = data.get("matn", "")
    havola     = data.get("havola", "")
    tugma_nomi = data.get("tugma_nomi", "")
    rang       = data.get("rang", "yashil")

    emoji = RANG_EMOJI.get(rang, "🟢")

    # Inline tugma (kanalga yuboriladigan postda)
    tugma_kb = None
    if havola and tugma_nomi:
        tugma_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{emoji} {tugma_nomi}", url=havola)]
        ])

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=matn or "Yangi post!",
            reply_markup=tugma_kb,
        )
        await update.message.reply_text(
            f"Post kanalga yuborildi! {emoji} rangli tugma bilan.",
            reply_markup=main_kb(),
        )
    except Exception as e:
        await update.message.reply_text(
            f"Xatolik: {str(e)}\n\nBot kanalda admin ekanligini tekshiring!",
            reply_markup=main_kb(),
        )

# ─── MAIN ─────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    logger.info("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
