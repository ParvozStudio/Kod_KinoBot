import logging
from aiogram import Bot
from config import REQUIRED_CHANNELS


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi barcha majburiy kanallarga obuna bo'lganmi tekshiradi."""
    if not REQUIRED_CHANNELS:
        return True
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ("left", "kicked"):
                logging.warning(f"[SUB] {user_id} kanalga a'zo emas: {channel} (status={member.status})")
                return False
        except Exception as e:
            # Bu joyda xato chiqsa — odatda bot o'sha kanalga ADMIN qilib
            # qo'shilmagan, yoki kanal ID noto'g'ri.
            logging.error(f"[SUB] Kanal tekshirishda xato: {channel} -> {e}")
            return False
    return True
