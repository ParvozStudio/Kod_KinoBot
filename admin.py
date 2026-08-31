import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from config import CATEGORIES, OWNER_ID
from keyboards import admin_menu_kb, category_choice_kb, cancel_kb
from states import AddVideo, DeleteVideo, AddAdmin, RemoveAdmin, Broadcast

router = Router()


def admin_only(user_id: int) -> bool:
    return db.is_admin(user_id)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not admin_only(message.from_user.id):
        await message.answer("⛔️ Sizda admin panelga kirish huquqi yo'q.")
        return
    await state.clear()
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "adm_home")
async def cb_adm_home(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)
    await state.clear()
    await call.message.edit_text("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "adm_cancel")
async def cb_adm_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())


# ---------------- STIKER ID OLISH (yordamchi) ----------------

@router.message(F.sticker)
async def catch_sticker_id(message: Message, state: FSMContext):
    """Admin botga stiker yuborsa (hech qanday holatda bo'lmasa),
    uning file_id sini qaytaradi — .env ga qo'yish uchun qulay."""
    if not admin_only(message.from_user.id):
        return
    current_state = await state.get_state()
    if current_state is not None:
        return
    await message.answer(
        f"🆔 Stiker file_id:\n<code>{message.sticker.file_id}</code>\n\n"
        "Buni .env faylidagi kerakli STICKER_* o'zgaruvchisiga qo'ying."
    )


# ---------------- VIDEO QO'SHISH ----------------

@router.callback_query(F.data == "adm:add_video")
async def cb_add_video(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)
    await state.set_state(AddVideo.choosing_category)
    await call.message.edit_text("📂 Kategoriyani tanlang:", reply_markup=category_choice_kb())


@router.callback_query(AddVideo.choosing_category, F.data.startswith("adm_cat:"))
async def cb_choose_category(call: CallbackQuery, state: FSMContext):
    category = call.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(AddVideo.waiting_title)
    await call.message.edit_text(
        f"Kategoriya: {CATEGORIES[category]}\n\n🎬 Endi video nomini yuboring:",
        reply_markup=cancel_kb(),
    )


@router.message(AddVideo.waiting_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddVideo.waiting_description)
    await message.answer(
        "📝 Endi qisqa tavsif yuboring (kerak bo'lmasa \"-\" deb yozing):",
        reply_markup=cancel_kb(),
    )


@router.message(AddVideo.waiting_description)
async def process_description(message: Message, state: FSMContext):
    desc = message.text.strip()
    await state.update_data(description=None if desc == "-" else desc)
    await state.set_state(AddVideo.waiting_code)
    await message.answer(
        "🔑 Endi bu video uchun <b>noyob kod</b> kiriting (masalan: <code>1234</code>):",
        reply_markup=cancel_kb(),
    )


@router.message(AddVideo.waiting_code)
async def process_code_input(message: Message, state: FSMContext):
    code = message.text.strip()
    if not code:
        await message.answer("❗️ Bo'sh kod bo'lishi mumkin emas. Qaytadan yuboring:", reply_markup=cancel_kb())
        return
    existing = db.get_video_by_code(code)
    if existing:
        await message.answer(
            f"❌ <b>\"{code}\"</b> kodi allaqachon band (\"{existing['title']}\"). "
            "Boshqa kod kiriting:",
            reply_markup=cancel_kb(),
        )
        return
    await state.update_data(code=code)
    await state.set_state(AddVideo.waiting_file)
    await message.answer("🎥 Endi video faylni yuboring (yoki forward qiling):", reply_markup=cancel_kb())


@router.message(AddVideo.waiting_file, F.video)
async def process_video_file(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        video_id = db.add_video(
            code=data["code"],
            category=data["category"],
            title=data["title"],
            description=data.get("description"),
            file_id=message.video.file_id,
            added_by=message.from_user.id,
        )
    except db.DuplicateCodeError:
        await message.answer(
            "❌ Bu orada kod band bo'lib qoldi (boshqa admin qo'shgan bo'lishi mumkin). "
            "Qaytadan /admin dan boshlang."
        )
        await state.clear()
        return

    await state.clear()
    await message.answer(
        "✅ <b>Video muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🆔 ID: {video_id}\n"
        f"📂 Kategoriya: {CATEGORIES[data['category']]}\n"
        f"🎬 Nomi: {data['title']}\n"
        f"🔑 Kod: <code>{data['code']}</code>",
        reply_markup=admin_menu_kb(),
    )


@router.message(AddVideo.waiting_file)
async def process_video_file_wrong(message: Message):
    await message.answer("❗️ Iltimos video fayl yuboring (rasm yoki matn emas).", reply_markup=cancel_kb())


# ---------------- VIDEO O'CHIRISH ----------------

@router.callback_query(F.data == "adm:del_video")
async def cb_del_video_prompt(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)
    await state.set_state(DeleteVideo.waiting_code)
    await call.message.edit_text(
        "🗑 O'chirmoqchi bo'lgan videoning <b>kodini</b> yuboring:",
        reply_markup=cancel_kb(),
    )


@router.message(DeleteVideo.waiting_code)
async def process_delete_code(message: Message, state: FSMContext):
    code = message.text.strip()
    video = db.get_video_by_code(code)
    await state.clear()
    if not video:
        await message.answer(
            f"❌ <b>\"{code}\"</b> kodi bo'yicha video topilmadi.",
            reply_markup=admin_menu_kb(),
        )
        return
    db.delete_video_by_code(code)
    await message.answer(
        f"🗑 <b>\"{video['title']}\"</b> (kod: <code>{code}</code>) o'chirildi.",
        reply_markup=admin_menu_kb(),
    )


# ---------------- ADMIN QO'SHISH / O'CHIRISH ----------------

@router.callback_query(F.data == "adm:add_admin")
async def cb_add_admin_prompt(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)
    await state.set_state(AddAdmin.waiting_id)
    await call.message.edit_text(
        "👤 Yangi adminning Telegram user_id raqamini yuboring.\n"
        "(ID ni @userinfobot orqali bilib olish mumkin)",
        reply_markup=cancel_kb(),
    )


@router.message(AddAdmin.waiting_id)
async def process_add_admin(message: Message, state: FSMContext):
    await state.clear()
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❗️ Faqat raqam (ID) yuboring.", reply_markup=admin_menu_kb())
        return
    new_admin_id = int(text)
    db.add_admin(new_admin_id, message.from_user.id)
    await message.answer(f"✅ {new_admin_id} endi admin.", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "adm:del_admin")
async def cb_del_admin_prompt(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)
    admins = db.get_admins()
    text = "👥 Hozirgi adminlar:\n" + "\n".join(f"• {a}" for a in admins)
    text += "\n\nO'chirmoqchi bo'lgan adminning ID raqamini yuboring:"
    await state.set_state(RemoveAdmin.waiting_id)
    await call.message.edit_text(text, reply_markup=cancel_kb())


@router.message(RemoveAdmin.waiting_id)
async def process_remove_admin(message: Message, state: FSMContext):
    await state.clear()
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❗️ Faqat raqam (ID) yuboring.", reply_markup=admin_menu_kb())
        return
    target_id = int(text)
    if target_id == OWNER_ID:
        await message.answer("❌ Bosh adminni o'chirib bo'lmaydi.", reply_markup=admin_menu_kb())
        return
    db.remove_admin(target_id)
    await message.answer(f"✅ {target_id} adminlikdan chiqarildi.", reply_markup=admin_menu_kb())


# ---------------- STATISTIKA ----------------

@router.callback_query(F.data == "adm:stats")
async def cb_stats(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)

    s = db.get_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {s['total_users']}\n"
        f"🎬 Videolar soni: {s['total_videos']}\n"
        f"👁 Jami ko'rishlar: {s['total_views']}\n\n"
        "<b>Kategoriyalar bo'yicha:</b>\n"
    )
    for cat, label in CATEGORIES.items():
        count = s["by_category"].get(cat, 0)
        text += f"{label}: {count}\n"

    if s["top_videos"]:
        text += "\n<b>🔥 Top 5 ko'rilgan video:</b>\n"
        for title, code, views in s["top_videos"]:
            text += f"• {title} (kod: {code}) — {views} ko'rish\n"

    await call.message.edit_text(text, reply_markup=admin_menu_kb())


# ---------------- BROADCAST ----------------

@router.callback_query(F.data == "adm:broadcast")
async def cb_broadcast_prompt(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return await call.answer("⛔️ Ruxsat yo'q", show_alert=True)
    await state.set_state(Broadcast.waiting_message)
    await call.message.edit_text(
        "📣 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni yozing "
        "(matn, rasm yoki video bo'lishi mumkin):",
        reply_markup=cancel_kb(),
    )


@router.message(Broadcast.waiting_message)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = db.get_all_user_ids()
    sent, failed = 0, 0
    status_msg = await message.answer(f"⏳ Yuborilmoqda... 0/{len(user_ids)}")

    for i, uid in enumerate(user_ids, start=1):
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
        except Exception:
            failed += 1
        if i % 25 == 0:
            try:
                await status_msg.edit_text(f"⏳ Yuborilmoqda... {i}/{len(user_ids)}")
            except Exception:
                pass
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ Xabar yuborildi!\n\n✔️ Muvaffaqiyatli: {sent}\n❌ Xato: {failed}",
    )
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu_kb())
