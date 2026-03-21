import logging
import os
import json
import base64
import httpx
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, KeyboardButton, ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
)

# ─── SOZLAMALAR ───────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RANG_EMOJI = {
    "yashil":"🟢","qizil":"🔴","kok":"🔵","sariq":"🟡",
    "toq_sariq":"🟠","binafsha":"🟣","qora":"⚫","oq":"⚪","jigarrang":"🟤",
}

# ─── ASOSIY MENYU ─────────────────────────────
def main_kb():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📝 Post yaratish", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
    )

# ─── RANGLI TUGMA BILAN XABAR YUBORISH ───────
async def send_with_style(method, chat_id, reply_markup_dict, **kwargs):
    payload = {"chat_id": chat_id, **kwargs}
    if reply_markup_dict:
        payload["reply_markup"] = json.dumps(reply_markup_dict)
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{API}/{method}", data=payload)
        return resp.json()

async def send_file_with_style(method, chat_id, field_name, file_bytes, filename, reply_markup_dict, **kwargs):
    payload = {"chat_id": chat_id, **kwargs}
    if reply_markup_dict:
        payload["reply_markup"] = json.dumps(reply_markup_dict)
    files = {field_name: (filename, file_bytes)}
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{API}/{method}", data=payload, files=files)
        return resp.json()

# ─── /start ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xush kelibsiz!\n\nPost yaratish uchun tugmani bosing:",
        reply_markup=main_kb(),
    )

# ─── WEBAPP MA'LUMOTI ─────────────────────────
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        await update.message.reply_text("Xatolik: noto'g'ri format.")
        return

    matn        = data.get("matn", "") or "Yangi post!"
    havola      = data.get("havola", "")
    tugma_nomi  = data.get("tugma_nomi", "")
    rang        = data.get("rang", "yashil")
    style       = data.get("style", "success")
    media_type  = data.get("media_type", "none")
    media_b64   = data.get("media_base64")
    stiker_id   = data.get("stiker_id", "")
    emoji       = RANG_EMOJI.get(rang, "🟢")

    # Inline tugma (rangli style bilan)
    reply_markup = None
    if havola and tugma_nomi:
        reply_markup = {
            "inline_keyboard": [[{
                "text": f"{emoji} {tugma_nomi}",
                "url": havola,
                "style": style
            }]]
        }

    try:
        result = None

        # 1. STIKER
        if media_type == "stiker" and stiker_id:
            result = await send_with_style(
                "sendSticker", CHANNEL_ID, None,
                sticker=stiker_id
            )
            # Stiker dan keyin matn + tugma
            if matn or reply_markup:
                result = await send_with_style(
                    "sendMessage", CHANNEL_ID, reply_markup,
                    text=matn
                )

        # 2. RASM
        elif media_type == "photo" and media_b64:
            # base64 dan bytes ga
            header, encoded = media_b64.split(",", 1)
            file_bytes = base64.b64decode(encoded)
            ext = "jpg"
            if "png" in header: ext = "png"
            elif "gif" in header: ext = "gif"
            result = await send_file_with_style(
                "sendPhoto", CHANNEL_ID,
                "photo", file_bytes, f"photo.{ext}",
                reply_markup,
                caption=matn if matn != "Yangi post!" else ""
            )

        # 3. VIDEO
        elif media_type == "video" and media_b64:
            header, encoded = media_b64.split(",", 1)
            file_bytes = base64.b64decode(encoded)
            result = await send_file_with_style(
                "sendVideo", CHANNEL_ID,
                "video", file_bytes, "video.mp4",
                reply_markup,
                caption=matn if matn != "Yangi post!" else ""
            )

        # 4. FAQAT MATN
        else:
            result = await send_with_style(
                "sendMessage", CHANNEL_ID, reply_markup,
                text=matn
            )

        if result and result.get("ok"):
            await update.message.reply_text(
                f"✅ Post kanalga yuborildi!\n{emoji} rangli tugma bilan.",
                reply_markup=main_kb(),
            )
        else:
            err = result.get("description", "Nomalum xato") if result else "Javob kelmadi"
            await update.message.reply_text(
                f"❌ Xato: {err}\n\nBot kanalda admin ekanligini tekshiring!",
                reply_markup=main_kb(),
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Xato: {str(e)}",
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
