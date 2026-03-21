import logging
import os
import json
import httpx
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ─── SOZLAMALAR ───────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── STYLE TUGMA BILAN POST YUBORISH ──────────
async def send_post_with_style(chat_id, text, buttons):
    """
    buttons = [
      {"text": "Buyurtma berish", "url": "https://...", "style": "success"},
      {"text": "Orqaga",          "url": "https://...", "style": "danger"},
    ]
    style: success=yashil, primary=ko'k, danger=qizil
    """
    inline_keyboard = []
    for btn in buttons:
        row = {"text": btn["text"], "url": btn.get("url", "")}
        if "style" in btn:
            row["style"] = btn["style"]
        inline_keyboard.append([row])

    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps({"inline_keyboard": inline_keyboard}),
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API}/sendMessage", data=payload)
        return resp.json()

# ─── ASOSIY MENYU ─────────────────────────────
def main_kb():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📝 Post yaratish", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
    )

# ─── /start ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xush kelibsiz!\n\nPost yaratish uchun tugmani bosing:",
        reply_markup=main_kb(),
    )

# ─── /test — rangli tugmalarni sinash ─────────
async def test_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await send_post_with_style(
        chat_id=update.message.chat_id,
        text="Rangli tugmalar sinovi:",
        buttons=[
            {"text": "🟢 Yashil tugma", "url": "https://t.me/Azizbekl2026", "style": "success"},
            {"text": "🔵 Ko'k tugma",   "url": "https://t.me/Azizbekl2026", "style": "primary"},
            {"text": "🔴 Qizil tugma",  "url": "https://t.me/Azizbekl2026", "style": "danger"},
        ]
    )
    if result.get("ok"):
        await update.message.reply_text("✅ Rangli tugmalar yuborildi!")
    else:
        await update.message.reply_text(f"❌ Xato: {result}")

# ─── WEBAPP DAN KELGAN MA'LUMOT ───────────────
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        await update.message.reply_text("Xatolik!")
        return

    matn       = data.get("matn", "Yangi post!")
    havola     = data.get("havola", "https://t.me/Azizbekl2026")
    tugma_nomi = data.get("tugma_nomi", "Buyurtma berish")
    rang       = data.get("rang", "yashil")

    # rang → style
    style_map = {
        "yashil":    "success",
        "qizil":     "danger",
        "kok":       "primary",
        "sariq":     "primary",
        "toq_sariq": "primary",
        "binafsha":  "primary",
        "qora":      "primary",
        "oq":        "primary",
        "jigarrang": "primary",
    }
    style = style_map.get(rang, "success")

    result = await send_post_with_style(
        chat_id=CHANNEL_ID,
        text=matn,
        buttons=[
            {"text": tugma_nomi, "url": havola, "style": style},
        ]
    )

    if result.get("ok"):
        await update.message.reply_text(
            "✅ Post kanalga rangli tugma bilan yuborildi!",
            reply_markup=main_kb(),
        )
    else:
        await update.message.reply_text(
            f"❌ Xato: {result.get('description', 'Nomalum xato')}\n"
            "Bot kanalda admin ekanligini tekshiring!",
            reply_markup=main_kb(),
        )

# ─── MAIN ─────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    logger.info("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
