import logging, os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import WebAppInfo

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def post_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Post yaratish", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Xush kelibsiz!</b>\n\n📢 Kanalga post yuborish uchun tugmani bosing:",
        parse_mode="HTML",
        reply_markup=post_kb()
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
