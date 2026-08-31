from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CATEGORIES, REQUIRED_CHANNELS


async def subscribe_kb(bot) -> InlineKeyboardMarkup:
    """Majburiy obuna kanallari uchun tugmalar. Har bir kanal uchun to'g'ri
    havola (public bo'lsa @username, private bo'lsa Telegram'dan olingan
    invite_link) ishlatiladi — kanal ID hech qachon foydalanuvchiga ko'rsatilmaydi.
    """
    b = InlineKeyboardBuilder()
    for ch in REQUIRED_CHANNELS:
        ch = str(ch).strip()
        url = None
        if ch.startswith("@"):
            url = f"https://t.me/{ch.lstrip('@')}"
        else:
            try:
                chat = await bot.get_chat(ch)
                url = chat.invite_link
                if not url:
                    link_obj = await bot.create_chat_invite_link(chat_id=ch)
                    url = link_obj.invite_link
            except Exception:
                url = None
        if url:
            b.button(text="➕ Obuna bo'lish", url=url)
    b.button(text="✅ Obuna bo'ldim", callback_data="check_sub")
    b.adjust(1)
    return b.as_markup()


def admin_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Video qo'shish", callback_data="adm:add_video")
    b.button(text="🗑 Video o'chirish", callback_data="adm:del_video")
    b.button(text="👤 Admin qo'shish", callback_data="adm:add_admin")
    b.button(text="👤 Admin o'chirish", callback_data="adm:del_admin")
    b.button(text="📊 Statistika", callback_data="adm:stats")
    b.button(text="📣 Xabar yuborish", callback_data="adm:broadcast")
    b.adjust(2, 2, 1, 1)
    return b.as_markup()


def category_choice_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        b.button(text=label, callback_data=f"adm_cat:{key}")
    b.adjust(2)
    return b.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="❌ Bekor qilish", callback_data="adm_cancel")
    return b.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🛠 Admin panel", callback_data="adm_home")
    return b.as_markup()
