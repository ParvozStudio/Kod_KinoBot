import logging
from aiogram import Bot

from config import STICKERS


async def send_sticker_safe(bot: Bot, chat_id: int, key: str):
    """STICKERS lug'atidan kalit bo'yicha stiker yuboradi.
    Agar file_id bo'sh yoki noto'g'ri bo'lsa, xatoni yutib yuboradi —
    bot stiker sabab to'xtab qolmasin.
    """
    file_id = STICKERS.get(key, "")
    if not file_id:
        return
    try:
        await bot.send_sticker(chat_id=chat_id, sticker=file_id)
    except Exception as e:
        logging.warning(f"Stiker yuborilmadi ({key}): {e}")
