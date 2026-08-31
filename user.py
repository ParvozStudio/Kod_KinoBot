from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from config import CATEGORIES
from keyboards import subscribe_kb
from states import WaitingCode
from subscription import check_subscription
from stickers import send_sticker_safe

router = Router()


WELCOME_TEXT = (
    "✨ <b>Xush kelibsiz!</b> ✨\n\n"
    "🎬 Bu yerda siz <b>kino</b>, <b>drama</b>, <b>serial</b>, <b>anime</b> va "
    "<b>multfilmlarni</b> maxsus <b>kod</b> orqali topishingiz mumkin!\n\n"
    "🔑 Pastdagi kanalga postlarni kuzatib boring — har bir kontent ostida "
    "uning kodi yozilgan bo'ladi.\n\n"
    "👇 Kodni shu yerga yozib yuboring:"
)


async def ask_for_code(bot: Bot, chat_id: int, state: FSMContext):
    await send_sticker_safe(bot, chat_id, "ask_code")
    await bot.send_message(
        chat_id,
        "🔑 <b>Kodni kiriting...</b>\n\n"
        "Masalan: <code>1234</code>",
    )
    await state.set_state(WaitingCode.active)


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if not await check_subscription(bot, message.from_user.id):
        await send_sticker_safe(bot, message.chat.id, "subscribe")
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun</b> quyidagi kanal(lar)ga obuna bo'ling, "
            "so'ng <b>✅ Obuna bo'ldim</b> tugmasini bosing:",
            reply_markup=await subscribe_kb(bot),
        )
        return

    await send_sticker_safe(bot, message.chat.id, "welcome")
    await message.answer(WELCOME_TEXT)
    await state.set_state(WaitingCode.active)


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(call: CallbackQuery, bot: Bot, state: FSMContext):
    if await check_subscription(bot, call.from_user.id):
        await call.message.delete()
        await send_sticker_safe(bot, call.message.chat.id, "welcome")
        await call.message.answer(WELCOME_TEXT)
        await state.set_state(WaitingCode.active)
    else:
        await call.answer("❌ Siz hali barcha kanal(lar)ga obuna bo'lmadingiz.", show_alert=True)


@router.message(WaitingCode.active)
async def process_code(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription(bot, message.from_user.id):
        await send_sticker_safe(bot, message.chat.id, "subscribe")
        await message.answer(
            "⚠️ Botdan foydalanish uchun avval kanal(lar)ga obuna bo'ling:",
            reply_markup=await subscribe_kb(bot),
        )
        return

    code = message.text.strip()
    video = db.get_video_by_code(code)

    if not video:
        await send_sticker_safe(bot, message.chat.id, "not_found")
        await message.answer(
            f"❌ <b>\"{code}\"</b> kodi bo'yicha hech qanday narsa topilmadi.\n\n"
            "🔁 Kodni tekshirib, qaytadan urinib ko'ring."
        )
        return

    db.increment_view(video["id"], message.from_user.id)

    label = CATEGORIES.get(video["category"], video["category"])
    caption = (
        f"{label}\n"
        f"🎬 <b>{video['title']}</b>\n"
        f"🔑 Kod: <code>{video['code']}</code>"
    )
    if video["description"]:
        caption += f"\n\n📝 {video['description']}"

    await send_sticker_safe(bot, message.chat.id, "found")
    await bot.send_video(
        chat_id=message.chat.id,
        video=video["file_id"],
        caption=caption,
    )
    await message.answer("🔑 Yana kod kiritsangiz bo'ladi:")
