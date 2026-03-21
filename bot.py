import logging, os, json, base64
import httpx
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RANG_EMOJI = {"yashil":"🟢","qizil":"🔴","kok":"🔵"}

def main_kb():
    """Xabar ichida ko'k inline tugma — WebApp ochadi"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "📝 Post yaratish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])

async def api_post(method, **kwargs):
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{API}/{method}", data=kwargs)
        return r.json()

async def api_file(method, field, fbytes, fname, **kwargs):
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{API}/{method}", data=kwargs, files={field:(fname,fbytes)})
        return r.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xush kelibsiz!\n\nKanalga post yuborish uchun quyidagi tugmani bosing:",
        reply_markup=main_kb(),
    )

async def webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        await update.message.reply_text("Xatolik!", reply_markup=main_kb())
        return

    matn       = data.get("matn","") or "Yangi post!"
    havola     = data.get("havola","")
    tugma_nomi = data.get("tugma_nomi","")
    rang       = data.get("rang","kok")
    style      = data.get("style","primary")
    media_type = data.get("media_type","none")
    media_b64  = data.get("media_base64")
    emoji      = RANG_EMOJI.get(rang,"🔵")

    rm = None
    if havola and tugma_nomi:
        rm = json.dumps({"inline_keyboard":[[{
            "text": f"{emoji} {tugma_nomi}",
            "url": havola,
            "style": style
        }]]})

    try:
        res = None
        if media_type == "photo" and media_b64:
            hdr, enc = media_b64.split(",",1)
            ext = "png" if "png" in hdr else "jpg"
            fb = base64.b64decode(enc)
            kw = {"chat_id": CHANNEL_ID}
            if matn != "Yangi post!": kw["caption"] = matn
            if rm: kw["reply_markup"] = rm
            res = await api_file("sendPhoto","photo",fb,f"p.{ext}",**kw)

        elif media_type == "video" and media_b64:
            hdr, enc = media_b64.split(",",1)
            fb = base64.b64decode(enc)
            kw = {"chat_id": CHANNEL_ID}
            if matn != "Yangi post!": kw["caption"] = matn
            if rm: kw["reply_markup"] = rm
            res = await api_file("sendVideo","video",fb,"v.mp4",**kw)

        else:
            kw = {"chat_id": CHANNEL_ID, "text": matn}
            if rm: kw["reply_markup"] = rm
            res = await api_post("sendMessage",**kw)

        if res and res.get("ok"):
            await update.message.reply_text(
                f"✅ Kanalga yuborildi! {emoji}",
                reply_markup=main_kb()
            )
        else:
            err = res.get("description","Xato") if res else "Javob yoq"
            await update.message.reply_text(f"❌ {err}", reply_markup=main_kb())

    except Exception as e:
        await update.message.reply_text(f"❌ {e}", reply_markup=main_kb())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_handler))
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
