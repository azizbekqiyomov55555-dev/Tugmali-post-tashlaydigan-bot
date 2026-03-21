import logging, os, json, base64
import httpx
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RANG_EMOJI = {"yashil":"🟢", "qizil":"🔴", "kok":"🔵"}
RANG_STYLE = {"yashil":"success", "qizil":"danger", "kok":"primary"}

async def tg(method, **kwargs):
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{API}/{method}", data=kwargs)
        res = r.json()
        logger.info(f"API {method} -> ok={res.get('ok')} {res.get('description','')}")
        return res

async def tg_file(method, field, fbytes, fname, **kwargs):
    logger.info(f"Uploading {fname} ({len(fbytes)} bytes)")
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{API}/{method}", data=kwargs, files={field:(fname, fbytes)})
        res = r.json()
        logger.info(f"API {method} -> ok={res.get('ok')} {res.get('description','')}")
        return res

def post_kb():
    return json.dumps({"inline_keyboard": [[{
        "text": "📝　　　　Post yaratish　　　　📝",
        "web_app": {"url": WEBAPP_URL},
        "style": "primary"
    }]]})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tg("sendMessage",
        chat_id=update.message.chat_id,
        text="👋 <b>Xush kelibsiz!</b>\n\n📢 Kanalga post yuborish uchun tugmani bosing:",
        parse_mode="HTML",
        reply_markup=post_kb()
    )

async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

async def webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    logger.info(f"webapp_handler from {chat_id}")

    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception as e:
        logger.error(f"JSON error: {e}")
        await tg("sendMessage", chat_id=chat_id, text=f"❌ Xatolik: {e}")
        return

    matn       = data.get("matn","").strip()
    havola     = data.get("havola","").strip()
    tugma_nomi = data.get("tugma_nomi","").strip()
    rang       = data.get("rang","kok")
    media_type = data.get("media_type","none")
    media_b64  = data.get("media_base64")
    video_url  = data.get("video_url","")
    emoji      = RANG_EMOJI.get(rang,"🔵")
    style      = RANG_STYLE.get(rang,"primary")

    logger.info(f"media_type={media_type} matn={bool(matn)} havola={bool(havola)} tugma={bool(tugma_nomi)}")

    # Kanal tugmasi
    rm = None
    if havola and tugma_nomi:
        rm = json.dumps({"inline_keyboard": [[
            {"text": f"{emoji} {tugma_nomi}", "url": havola, "style": style}
        ]]})

    post_text = matn if matn else "📢 Yangi post!"

    try:
        res = None

        # RASM
        if media_type == "photo" and media_b64:
            try:
                enc = media_b64.split(",",1)[1] if "," in media_b64 else media_b64
                fb = base64.b64decode(enc)
                ext = "png" if "png" in media_b64[:30] else "jpg"
            except Exception as e:
                await tg("sendMessage", chat_id=chat_id, text=f"❌ Rasm xatosi: {e}")
                return
            kw = {"chat_id": CHANNEL_ID}
            if matn: kw["caption"] = matn
            if rm: kw["reply_markup"] = rm
            res = await tg_file("sendPhoto", "photo", fb, f"photo.{ext}", **kw)

        # VIDEO URL
        elif media_type == "video_url" and video_url:
            kw = {"chat_id": CHANNEL_ID, "text": post_text, "parse_mode": "HTML"}
            if rm: kw["reply_markup"] = rm
            res = await tg("sendMessage", **kw)

        # FAQAT MATN
        else:
            kw = {"chat_id": CHANNEL_ID, "text": post_text, "parse_mode": "HTML"}
            if rm: kw["reply_markup"] = rm
            res = await tg("sendMessage", **kw)

        if res and res.get("ok"):
            await tg("sendMessage", chat_id=chat_id,
                     text=f"✅ Kanalga yuborildi! {emoji}", reply_markup=post_kb())
        else:
            err = res.get("description","Nomalum xato") if res else "Javob kelmadi"
            await tg("sendMessage", chat_id=chat_id,
                     text=f"❌ Xato: {err}\n\nBot kanalda <b>admin</b> ekanligini tekshiring!",
                     parse_mode="HTML", reply_markup=post_kb())

    except Exception as e:
        logger.exception(e)
        await tg("sendMessage", chat_id=chat_id, text=f"❌ {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(noop))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_handler))
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
