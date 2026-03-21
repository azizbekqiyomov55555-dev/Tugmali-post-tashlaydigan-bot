import logging, os, json, base64
import httpx
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "8620251558:AAFtCwV29iHcTR5TfeWmBNCAWSjPl2ZcK6c")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@Azizbekl2026")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://azizbekqiyomov55555-dev.github.io/Tugmali-post-tashlaydigan-bot/webapp.html")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

RANG_EMOJI = {"yashil":"🟢", "qizil":"🔴", "kok":"🔵"}
RANG_STYLE = {"yashil":"success", "qizil":"danger", "kok":"primary"}

async def tg(method, **kwargs):
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{API}/{method}", data=kwargs)
        result = r.json()
        logger.info(f"tg.{method} → {result}")
        return result

async def tg_file(method, field, fbytes, fname, **kwargs):
    logger.info(f"tg_file.{method} file={fname} size={len(fbytes)}")
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{API}/{method}", data=kwargs, files={field:(fname, fbytes)})
        result = r.json()
        logger.info(f"tg_file.{method} → {result}")
        return result

def post_kb():
    keyboard = [[{
        "text": "📝　　　　Post yaratish　　　　📝",
        "web_app": {"url": WEBAPP_URL},
        "style": "primary"
    }]]
    return json.dumps({"inline_keyboard": keyboard})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tg(
        "sendMessage",
        chat_id=update.message.chat_id,
        text=(
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 <b>Kanal uchun post yarating!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Matn yozing\n"
            "🖼 Rasm yoki video qo'shing\n"
            "🔗 Havola va tugma qo'shing\n"
            "🎨 Tugma rangini tanlang\n\n"
            "⬇️ <b>Quyidagi tugmani bosing:</b>"
        ),
        parse_mode="HTML",
        reply_markup=post_kb()
    )

async def noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

async def webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    logger.info(f"webapp_handler called by chat_id={chat_id}")

    try:
        raw = update.message.web_app_data.data
        logger.info(f"raw data length={len(raw)}")
        data = json.loads(raw)
        logger.info(f"parsed data keys={list(data.keys())}")
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        await tg("sendMessage", chat_id=chat_id, text=f"❌ Ma'lumot xatosi: {e}")
        return

    matn       = data.get("matn", "").strip()
    havola     = data.get("havola", "").strip()
    tugma_nomi = data.get("tugma_nomi", "").strip()
    rang       = data.get("rang", "kok")
    media_type = data.get("media_type", "none")
    media_b64  = data.get("media_base64")
    emoji      = RANG_EMOJI.get(rang, "🔵")
    style      = RANG_STYLE.get(rang, "primary")

    logger.info(f"matn={matn[:30] if matn else ''} havola={havola} tugma={tugma_nomi} rang={rang} media={media_type}")

    # Kanal post tugmasi
    rm = None
    if havola and tugma_nomi:
        rm = json.dumps({"inline_keyboard": [[
            {"text": f"{emoji} {tugma_nomi}", "url": havola, "style": style}
        ]]})

    post_matn = matn if matn else "📢 Yangi post!"

    try:
        res = None

        if media_type == "photo" and media_b64:
            logger.info("Sending photo...")
            try:
                if "," in media_b64:
                    hdr, enc = media_b64.split(",", 1)
                else:
                    enc = media_b64
                    hdr = ""
                ext = "png" if "png" in hdr else "jpg"
                fb = base64.b64decode(enc)
                logger.info(f"Photo decoded: {len(fb)} bytes, ext={ext}")
            except Exception as e:
                logger.error(f"Photo decode error: {e}")
                await tg("sendMessage", chat_id=chat_id, text=f"❌ Rasm xatosi: {e}")
                return

            kw = {"chat_id": CHANNEL_ID}
            if matn:
                kw["caption"] = matn
                kw["parse_mode"] = "HTML"
            if rm:
                kw["reply_markup"] = rm
            res = await tg_file("sendPhoto", "photo", fb, f"photo.{ext}", **kw)

        elif media_type == "video" and media_b64:
            logger.info("Sending video...")
            try:
                if "," in media_b64:
                    _, enc = media_b64.split(",", 1)
                else:
                    enc = media_b64
                fb = base64.b64decode(enc)
                logger.info(f"Video decoded: {len(fb)} bytes")
            except Exception as e:
                logger.error(f"Video decode error: {e}")
                await tg("sendMessage", chat_id=chat_id, text=f"❌ Video xatosi: {e}")
                return

            kw = {"chat_id": CHANNEL_ID}
            if matn:
                kw["caption"] = matn
                kw["parse_mode"] = "HTML"
            if rm:
                kw["reply_markup"] = rm
            res = await tg_file("sendVideo", "video", fb, "video.mp4", **kw)

        else:
            logger.info("Sending text message...")
            kw = {"chat_id": CHANNEL_ID, "text": post_matn, "parse_mode": "HTML"}
            if rm:
                kw["reply_markup"] = rm
            res = await tg("sendMessage", **kw)

        if res and res.get("ok"):
            logger.info("Post sent successfully!")
            await tg(
                "sendMessage",
                chat_id=chat_id,
                text=f"✅ Post kanalga yuborildi! {emoji}",
                reply_markup=post_kb()
            )
        else:
            err = res.get("description", "Nomalum xato") if res else "Javob kelmadi"
            logger.error(f"Send failed: {err}")
            await tg(
                "sendMessage",
                chat_id=chat_id,
                text=f"❌ Xato: {err}",
                reply_markup=post_kb()
            )

    except Exception as e:
        logger.exception(f"webapp_handler exception: {e}")
        await tg("sendMessage", chat_id=chat_id, text=f"❌ Xato: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(noop))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_handler))
    logger.info("✅ Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
