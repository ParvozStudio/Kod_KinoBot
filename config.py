import os

# ============================================================
# BOT SOZLAMALARI — barcha qiymatlarni shu yerga to'g'ridan-to'g'ri yozing
# ============================================================

# Telegram bot token (BotFather'dan olinadi)
BOT_TOKEN = "8836112594:AAHmUfcQQaBvxP3JIVyJNm5rRXjhh-HGddQ"

# Bosh adminning Telegram user_id raqami (@userinfobot orqali bilib oling)
OWNER_ID = 8319291440

# Majburiy obuna kanallari ro'yxati.
# @username (ochiq kanal) yoki -100xxxxxxxxxx (yopiq kanal ID) formatida.
# Bo'sh ro'yxat qoldirsangiz, majburiy obuna o'chirilgan bo'ladi.
# Misol: REQUIRED_CHANNELS = ["@kanalim", "-1001234567890"]
REQUIRED_CHANNELS = [-1004311520707, -1004478817292, -1002580095478]

DB_PATH = "kodbot.db"

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
# stikerning file_id sini yozib beradi. Shu ID ni pastdagi qatorlarga qo'ying.
# Bo'sh qoldirsangiz, o'sha joyda stiker yuborilmaydi (xato bermaydi).
STICKERS = {
    "welcome": "",      # /start da, obuna bo'lganidan keyin
    "ask_code": "",     # "kodni kiriting" xabari bilan
    "found": "",        # kod topilganda
    "not_found": "",    # kod topilmaganda
    "subscribe": "",    # majburiy obuna xabarida
}
