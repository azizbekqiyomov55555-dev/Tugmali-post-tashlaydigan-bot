import logging, os, json, base64
import httpx
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RANG_EMOJI  = {"yashil":"🟢", "qizil":"🔴", "kok":"🔵"}
RANG_STYLE  = {"yashil":"success", "qizil":"danger", "kok":"primary"}

# ─── HTTP so'rov ──────────────────────────────
async def tg(method, **kwargs):
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{API}/{method}", data=kwargs)
        return r.json()

async def tg_file(method, field, fbytes, fname, **kwargs):
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{API}/{method}", data=kwargs, files={field:(fname,fbytes)})
        return r.json()

# ─── Ko'k rangli "Post yaratish" tugmasi ──────
def post_kb():
    """
    style='primary' → ko'k rang
    InlineKeyboardButton + WebApp
    """
    keyboard = [[{
        "text": "📝 Post yaratish",
        "web_app": {"url": WEBAPP_URL},
        "style": "primary"          # <-- KO'K rang
    }]]
    return json.dumps({"inline_keyboard": keyboard})

# ─── /start ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tg(
        "sendMessage",
        chat_id=update.message.chat_id,
        text="👋 <b>Xush kelibsiz!</b>\n\nKanalga post yuborish uchun tugmani bosing:",
        parse_mode="HTML",
        reply_markup=post_kb()
    )

# ─── Callback noop ────────────────────────────
async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

# ─── WebApp ma'lumoti ─────────────────────────
async def webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        await tg("sendMessage", chat_id=update.message.chat_id, text="Xatolik!")
        return

    matn       = data.get("matn","") or "Yangi post!"
    havola     = data.get("havola","")
    tugma_nomi = data.get("tugma_nomi","")
    rang       = data.get("rang","kok")
    media_type = data.get("media_type","none")
    media_b64  = data.get("media_base64")
    emoji      = RANG_EMOJI.get(rang, "🔵")
    style      = RANG_STYLE.get(rang, "primary")

    # Kanalga yuboriladigan rangli tugma
    rm = None
    if havola and tugma_nomi:
        rm = json.dumps({"inline_keyboard": [[{
            "text":  f"{emoji} {tugma_nomi}",
            "url":   havola,
            "style": style          # <-- RANGLI tugma
        }]]})

    try:
        res = None

        if media_type == "photo" and media_b64:
            hdr, enc = media_b64.split(",", 1)
            ext = "png" if "png" in hdr else "jpg"
            fb = base64.b64decode(enc)
            kw = {"chat_id": CHANNEL_ID}
            if matn != "Yangi post!": kw["caption"] = matn
            if rm: kw["reply_markup"] = rm
            res = await tg_file("sendPhoto", "photo", fb, f"p.{ext}", **kw)

        elif media_type == "video" and media_b64:
            hdr, enc = media_b64.split(",", 1)
            fb = base64.b64decode(enc)
            kw = {"chat_id": CHANNEL_ID}
            if matn != "Yangi post!": kw["caption"] = matn
            if rm: kw["reply_markup"] = rm
            res = await tg_file("sendVideo", "video", fb, "v.mp4", **kw)

        else:
            kw = {"chat_id": CHANNEL_ID, "text": matn}
            if rm: kw["reply_markup"] = rm
            res = await tg("sendMessage", **kw)

        if res and res.get("ok"):
            await tg(
                "sendMessage",
                chat_id=update.message.chat_id,
                text=f"✅ Kanalga yuborildi! {emoji}",
                reply_markup=post_kb()
            )
        else:
            err = res.get("description", "Xato") if res else "Javob yoq"
            await tg(
                "sendMessage",
                chat_id=update.message.chat_id,
                text=f"❌ {err}\nBot kanalda admin ekanligini tekshiring!",
                reply_markup=post_kb()
            )

    except Exception as e:
        await tg("sendMessage", chat_id=update.message.chat_id, text=f"❌ {e}")

# ─── MAIN ─────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(noop))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_handler))
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
