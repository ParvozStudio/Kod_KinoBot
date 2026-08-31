import os

from dotenv import load_dotenv

# Lokal kompyuterda ishga tushirganda .env faylidagi qiymatlarni o'qiydi.
# Railway'da bu chaqiruv shunchaki hech narsa qilmaydi — u o'z Variables
# panelidagi qiymatlarni avtomatik environment'ga qo'yib beradi.
load_dotenv()

# ============================================================
# BOT SOZLAMALARI — barcha qiymatlar Railway "Variables" (yoki lokal .env)
# orqali beriladi, bu faylda hech qanday maxfiy narsa yozilmaydi
# ============================================================

# Telegram bot token (BotFather'dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bosh adminning Telegram user_id raqami (@userinfobot orqali bilib oling)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Majburiy obuna kanallari ro'yxati.
# .env / Railway'da vergul bilan ajratib yoziladi, masalan:
# REQUIRED_CHANNELS=-1004311520707,-1004478817292,@kanalim
_raw_channels = os.getenv("REQUIRED_CHANNELS", "")
REQUIRED_CHANNELS = [
    ch.strip() for ch in _raw_channels.split(",") if ch.strip()
]

DB_PATH = os.getenv("DB_PATH", "kodbot.db")

# Kontent kategoriyalari
CATEGORIES = {
    "kino": "🎬 Kino",
    "drama": "🎭 Drama",
    "serial": "📺 Serial",
    "anime": "🇯🇵 Anime",
    "multfilm": "🧸 Multfilm",
}

# --- STIKERLAR ---
# Har bir voqea uchun ishlatiladigan stiker file_id lari.
# Buni to'ldirish uchun: botga istalgan stikerni yuboring (hech qanday
# menyu/holat ochiq bo'lmasa) — admin bo'lsangiz, bot sizga o'sha
# stikerning file_id sini yozib beradi. Shu ID ni Railway Variables'ga
# (yoki .env'ga) tegishli STICKER_* nomi bilan qo'ying.
STICKERS = {
    "welcome": os.getenv("STICKER_WELCOME", ""),      # /start da, obuna bo'lganidan keyin
    "ask_code": os.getenv("STICKER_ASK_CODE", ""),    # "kodni kiriting" xabari bilan
    "found": os.getenv("STICKER_FOUND", ""),          # kod topilganda
    "not_found": os.getenv("STICKER_NOT_FOUND", ""),  # kod topilmaganda
    "subscribe": os.getenv("STICKER_SUBSCRIBE", ""),  # majburiy obuna xabarida
}
