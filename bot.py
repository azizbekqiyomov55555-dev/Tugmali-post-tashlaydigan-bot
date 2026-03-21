import logging, os, httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    # Telegram API'ga to'g'ridan-to'g'ri murojaat (Tugma 100% ko'k bo'lishi uchun)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "👋 <b>Xush kelibsiz!</b>\n\n📢 Kanalga post yuborish uchun pastdagi tugmani bosing:",
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{
                "text": "📝       Post yaratish       📝",
                "web_app": {"url": WEBAPP_URL},
                "style": "primary" # BOT TUGMASI KO'K RANGDA BO'LADI
            }]]
        }
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
