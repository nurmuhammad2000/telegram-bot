import yt_dlp
import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = os.getenv("8658938325:AAHlU37sQLk6B4nF-t8wlX-MQyYUcvjpdVk")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# === TILLAR ===
LANGS = {
    "uz": {
        "start": "🎬 Salom! Video yoki audio link yuboring.\n\nQo'llab-quvvatlanadigan platformalar:\nYouTube, TikTok, Instagram, Facebook, Twitter, Pinterest va boshqalar.",
        "choose": "📥 Nima yuklamoqchisiz?",
        "video": "🎬 Video (MP4)",
        "audio": "🎵 Audio (MP3)",
        "downloading": "⏳",
        "done_video": "✅ Video tayyor!",
        "done_audio": "✅ Audio tayyor!",
        "error": "❌ Yuklab bo'lmadi. Link to'g'ri ekanligini tekshiring.",
        "not_url": "❗ Faqat video link yuboring.",
        "help": "ℹ️ Istalgan video linkini yuboring, men yuklab beraman!\n\n/start — Botni qayta ishga tushirish\n/help — Yordam\n/lang — Til tanlash",
        "lang_choose": "🌐 Tilni tanlang:",
        "lang_set": "✅ Til o'zgartirildi!",
        "stats": "📊 Statistika:\n👤 Foydalanuvchilar: {users}\n📥 Yuklab olingan: {downloads}",
        "broadcast_usage": "❗ Ishlatilishi: /broadcast Xabar matni",
        "broadcast_done": "✅ {count} ta foydalanuvchiga yuborildi!",
        "not_admin": "❌ Siz admin emassiz!",
    },
    "ru": {
        "start": "🎬 Привет! Отправьте ссылку на видео или аудио.\n\nПоддерживаемые платформы:\nYouTube, TikTok, Instagram, Facebook, Twitter, Pinterest и другие.",
        "choose": "📥 Что хотите скачать?",
        "video": "🎬 Видео (MP4)",
        "audio": "🎵 Аудио (MP3)",
        "downloading": "⏳",
        "done_video": "✅ Видео готово!",
        "done_audio": "✅ Аудио готово!",
        "error": "❌ Не удалось скачать. Проверьте ссылку.",
        "not_url": "❗ Отправьте только ссылку на видео.",
        "help": "ℹ️ Отправьте ссылку на любое видео, я скачаю!\n\n/start — Перезапустить бота\n/help — Помощь\n/lang — Выбор языка",
        "lang_choose": "🌐 Выберите язык:",
        "lang_set": "✅ Язык изменён!",
        "stats": "📊 Статистика:\n👤 Пользователей: {users}\n📥 Скачано: {downloads}",
        "broadcast_usage": "❗ Использование: /broadcast Текст сообщения",
        "broadcast_done": "✅ Отправлено {count} пользователям!",
        "not_admin": "❌ Вы не администратор!",
    },
    "en": {
        "start": "🎬 Hello! Send a video or audio link.\n\nSupported platforms:\nYouTube, TikTok, Instagram, Facebook, Twitter, Pinterest and more.",
        "choose": "📥 What do you want to download?",
        "video": "🎬 Video (MP4)",
        "audio": "🎵 Audio (MP3)",
        "downloading": "⏳",
        "done_video": "✅ Video ready!",
        "done_audio": "✅ Audio ready!",
        "error": "❌ Failed to download. Please check the link.",
        "not_url": "❗ Please send only a video link.",
        "help": "ℹ️ Send any video link and I'll download it!\n\n/start — Restart bot\n/help — Help\n/lang — Choose language",
        "lang_choose": "🌐 Choose language:",
        "lang_set": "✅ Language changed!",
        "stats": "📊 Stats:\n👤 Users: {users}\n📥 Downloads: {downloads}",
        "broadcast_usage": "❗ Usage: /broadcast Message text",
        "broadcast_done": "✅ Sent to {count} users!",
        "not_admin": "❌ You are not admin!",
    }
}

# === MA'LUMOTLAR ===
user_langs = {}      # {user_id: "uz"/"ru"/"en"}
user_ids = set()     # barcha foydalanuvchilar
total_downloads = 0  # jami yuklab olinganlar
pending_urls = {}    # {user_id: url}

def get_lang(user_id):
    return user_langs.get(user_id, "uz")

def t(user_id, key, **kwargs):
    lang = get_lang(user_id)
    text = LANGS[lang].get(key, "")
    return text.format(**kwargs) if kwargs else text

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

# === BUYRUQLAR ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    await update.message.reply_text(t(user_id, "start"))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(t(user_id, "help"))

async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text(
        t(user_id, "lang_choose"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(t(user_id, "not_admin"))
        return
    await update.message.reply_text(
        t(user_id, "stats", users=len(user_ids), downloads=total_downloads)
    )

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(t(user_id, "not_admin"))
        return
    if not context.args:
        await update.message.reply_text(t(user_id, "broadcast_usage"))
        return
    text = " ".join(context.args)
    count = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            count += 1
        except:
            pass
    await update.message.reply_text(t(user_id, "broadcast_done", count=count))

# === LINK QABUL QILISH ===
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_downloads
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    url = update.message.text.strip()

    if not is_url(url):
        await update.message.reply_text(t(user_id, "not_url"))
        return

    pending_urls[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton(t(user_id, "video"), callback_data="dl_video"),
            InlineKeyboardButton(t(user_id, "audio"), callback_data="dl_audio"),
        ]
    ]
    await update.message.reply_text(
        t(user_id, "choose"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# === YUKLAB OLISH ===
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_downloads
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # Til tanlash
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_langs[user_id] = lang
        await query.edit_message_text(t(user_id, "lang_set"))
        return

    # Yuklab olish
    url = pending_urls.get(user_id)
    if not url:
        return

    await query.edit_message_text(t(user_id, "downloading"))

    file_name = f"file_{user_id}_{int(time.time())}"
    is_audio = data == "dl_audio"

    if is_audio:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": file_name + ".%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        out_file = file_name + ".mp3"
    else:
        ydl_opts = {
            "format": "mp4/best",
            "outtmpl": file_name + ".mp4",
        }
        out_file = file_name + ".mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.delete_message()

        if is_audio:
            with open(out_file, "rb") as f:
                await context.bot.send_audio(
                    chat_id=user_id,
                    audio=f,
                    caption=t(user_id, "done_audio")
                )
        else:
            with open(out_file, "rb") as f:
                await context.bot.send_video(
                    chat_id=user_id,
                    video=f,
                    supports_streaming=True,
                    caption=t(user_id, "done_video")
                )

        total_downloads += 1
        pending_urls.pop(user_id, None)

    except Exception as e:
        await context.bot.send_message(
            chat_id=user_id,
            text=t(user_id, "error")
        )
    finally:
        if os.path.exists(out_file):
            os.remove(out_file)


# === ISHGA TUSHIRISH ===
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("lang", lang_cmd))
app.add_handler(CommandHandler("stats", stats_cmd))
app.add_handler(CommandHandler("broadcast", broadcast_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(callback_handler))

print("Bot ishlayapti...")
app.run_polling()