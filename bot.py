import yt_dlp
import time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8658938325:AAEp1EhEA70aQJjWHdmX5MnmAwLMS4M89mo"


def is_url(text):
    return text.startswith("http")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📎 Video link yubor (YouTube / TikTok / Instagram)")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not is_url(url):
        await update.message.reply_text("❗ Faqat video link yuboring")
        return

    msg = await update.message.reply_text("⏳")

    # HAR SAFAR YANGI FILE NAME
    file_name = f"video_{int(time.time())}.mp4"

    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": file_name
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await msg.delete()

        await update.message.reply_video(
            video=open(file_name, "rb"),
            supports_streaming=True
        )

    except Exception as e:
        await msg.edit_text("❌ Videoni yuklab bo‘lmadi")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot ishlayapti...")
app.run_polling()