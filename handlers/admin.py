import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from config import ADMIN_IDS, STUDIO_NAME

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ---------------------------------------------------------------
# FSM HOLATLARI
# ---------------------------------------------------------------
class AddAnime(StatesGroup):
    title = State()
    description = State()
    genre = State()
    year = State()
    status = State()
    poster = State()


class AddEpisode(StatesGroup):
    anime_id = State()
    episode_number = State()
    video = State()


class EditAnime(StatesGroup):
    choose_anime = State()
    choose_field = State()
    new_value = State()


class DeleteAnime(StatesGroup):
    choose_anime = State()


class Broadcast(StatesGroup):
    waiting_message = State()


class AddChannel(StatesGroup):
    waiting_forward = State()
    waiting_invite_link = State()


# ---------------------------------------------------------------
# ADMIN PANEL KIRISH
# ---------------------------------------------------------------
@router.message(Command("admin"))
@router.message(F.text == "🛠 Admin panel")
async def open_admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        f"🛠 <b>{STUDIO_NAME} — Admin panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=kb.admin_menu_kb(),
    )


@router.message(
    F.text == "❌ Bekor qilish",
    StateFilter(AddAnime, AddEpisode, EditAnime, DeleteAnime, Broadcast, AddChannel),
)
async def cancel_any(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("Bekor qilindi. 🛠 Admin panel:", reply_markup=kb.admin_menu_kb())


# =================================================================
# ➕ ANIME QO'SHISH
# =================================================================
@router.message(F.text == "➕ Anime qo'shish")
async def add_anime_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddAnime.title)
    await message.answer("📝 Anime nomini kiriting:", reply_markup=kb.cancel_kb())


@router.message(AddAnime.title)
async def add_anime_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddAnime.description)
    await message.answer("📖 Qisqacha tavsif yuboring (yoki o'tkazib yuboring):", reply_markup=kb.skip_cancel_kb())


@router.message(AddAnime.description)
async def add_anime_description(message: Message, state: FSMContext):
    desc = "" if message.text == "⏭ O'tkazib yuborish" else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(AddAnime.genre)
    await message.answer("🏷 Janrini kiriting (masalan: Action, Fantasy):", reply_markup=kb.skip_cancel_kb())


@router.message(AddAnime.genre)
async def add_anime_genre(message: Message, state: FSMContext):
    genre = "" if message.text == "⏭ O'tkazib yuborish" else message.text.strip()
    await state.update_data(genre=genre)
    await state.set_state(AddAnime.year)
    await message.answer("📅 Chiqarilgan yilini kiriting (masalan: 2024):", reply_markup=kb.skip_cancel_kb())


@router.message(AddAnime.year)
async def add_anime_year(message: Message, state: FSMContext):
    if message.text == "⏭ O'tkazib yuborish":
        year = None
    else:
        year_text = message.text.strip()
        if not year_text.isdigit():
            await message.answer("❗️ Iltimos, yilni raqamda kiriting (masalan: 2024):")
            return
        year = int(year_text)
    await state.update_data(year=year)
    await state.set_state(AddAnime.status)
    await message.answer("📌 Holatini tanlang:", reply_markup=kb.status_choice_kb())


@router.callback_query(F.data.startswith("status_"), AddAnime.status)
async def add_anime_status(callback: CallbackQuery, state: FSMContext):
    status = callback.data.replace("status_", "")
    await state.update_data(status=status)
    await state.set_state(AddAnime.poster)
    await callback.message.answer("🖼 Poster rasmini yuboring (yoki o'tkazib yuboring):", reply_markup=kb.skip_cancel_kb())
    await callback.answer()


@router.message(AddAnime.poster, F.photo)
async def add_anime_poster_photo(message: Message, state: FSMContext):
    await state.update_data(poster=message.photo[-1].file_id)
    await finish_add_anime(message, state)


@router.message(AddAnime.poster, F.text == "⏭ O'tkazib yuborish")
async def add_anime_poster_skip(message: Message, state: FSMContext):
    await state.update_data(poster=None)
    await finish_add_anime(message, state)


@router.message(AddAnime.poster)
async def add_anime_poster_invalid(message: Message, state: FSMContext):
    await message.answer("❗️ Iltimos, rasm yuboring yoki ⏭ O'tkazib yuborish tugmasini bosing.")


async def finish_add_anime(message: Message, state: FSMContext):
    data = await state.get_data()
    anime_id = await db.add_anime(
        title=data["title"],
        description=data.get("description", ""),
        genre=data.get("genre", ""),
        year=data.get("year"),
        status=data.get("status", "Davom etmoqda"),
        poster=data.get("poster"),
    )
    await state.clear()
    await message.answer(
        f"✅ Anime muvaffaqiyatli qo'shildi!\n\n"
        f"🆔 ID: <code>{anime_id}</code>\n"
        f"📝 Nomi: {data['title']}\n\n"
        f"Endi shu ID orqali 🎬 Qism qo'shish bo'limidan video qismlarini yuklashingiz mumkin.",
        reply_markup=kb.admin_menu_kb(),
    )


# =================================================================
# 🎬 QISM QO'SHISH
# =================================================================
@router.message(F.text == "🎬 Qism qo'shish")
async def add_episode_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddEpisode.anime_id)
    await message.answer("🆔 Qism qo'shmoqchi bo'lgan anime ID sini kiriting:", reply_markup=kb.cancel_kb())


@router.message(AddEpisode.anime_id)
async def add_episode_anime_id(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗️ ID raqam bo'lishi kerak. Qaytadan kiriting:")
        return
    anime = await db.get_anime_by_id(int(message.text.strip()))
    if not anime:
        await message.answer("❗️ Bunday ID li anime topilmadi. Qaytadan kiriting:")
        return
    await state.update_data(anime_id=anime["id"], anime_title=anime["title"])
    await state.set_state(AddEpisode.episode_number)
    await message.answer(
        f"🎬 <b>{anime['title']}</b> uchun qism qo'shilmoqda.\n\nQism raqamini kiriting (masalan: 1):",
        reply_markup=kb.cancel_kb(),
    )


@router.message(AddEpisode.episode_number, F.text == "✅ Yakunlash")
async def add_episode_finish(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Qismlar qo'shish yakunlandi.", reply_markup=kb.admin_menu_kb())


@router.message(AddEpisode.episode_number)
async def add_episode_number(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❗️ Qism raqami butun son bo'lishi kerak:")
        return
    await state.update_data(episode_number=int(message.text.strip()))
    await state.set_state(AddEpisode.video)
    await message.answer("📹 Endi shu qismning video faylini yuboring:", reply_markup=kb.cancel_kb())


@router.message(AddEpisode.video, F.video)
async def add_episode_video(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_episode(data["anime_id"], data["episode_number"], message.video.file_id)
    await message.answer(
        f"✅ <b>{data['anime_title']}</b> — {data['episode_number']}-qism qo'shildi!\n\n"
        f"Yana qism qo'shish uchun raqamini kiriting, yoki tugatish uchun ✅ Yakunlash tugmasini bosing:",
        reply_markup=kb.finish_cancel_kb(),
    )
    await state.set_state(AddEpisode.episode_number)


@router.message(AddEpisode.video)
async def add_episode_video_invalid(message: Message):
    await message.answer("❗️ Iltimos, video fayl yuboring.")


# =================================================================
# ✏️ TAHRIRLASH
# =================================================================
@router.message(F.text == "✏️ Tahrirlash")
async def edit_anime_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(EditAnime.choose_anime)
    await message.answer("🆔 Tahrirlamoqchi bo'lgan anime ID sini kiriting:", reply_markup=kb.cancel_kb())


@router.message(EditAnime.choose_anime)
async def edit_anime_choose(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗️ ID raqam bo'lishi kerak:")
        return
    anime = await db.get_anime_by_id(int(message.text.strip()))
    if not anime:
        await message.answer("❗️ Bunday ID li anime topilmadi:")
        return
    await state.update_data(anime_id=anime["id"])
    await state.set_state(EditAnime.choose_field)
    await message.answer(
        f"✏️ <b>{anime['title']}</b>\n\nQaysi maydonni tahrirlaysiz?",
        reply_markup=kb.edit_fields_kb(anime["id"]),
    )


@router.callback_query(kb.EditFieldCB.filter(), EditAnime.choose_field)
async def edit_anime_field_chosen(callback: CallbackQuery, callback_data: kb.EditFieldCB, state: FSMContext):
    await state.update_data(field=callback_data.field)
    await state.set_state(EditAnime.new_value)
    field_names = {
        "title": "yangi nomni",
        "description": "yangi tavsifni",
        "genre": "yangi janrni",
        "year": "yangi yilni",
        "status": "yangi holatni",
        "poster": "yangi poster rasmni",
    }
    prompt = field_names.get(callback_data.field, "yangi qiymatni")
    await callback.message.answer(f"✍️ {prompt.capitalize()} yuboring:", reply_markup=kb.cancel_kb())
    await callback.answer()


@router.message(EditAnime.new_value, F.photo)
async def edit_anime_new_value_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("field") != "poster":
        await message.answer("❗️ Bu maydon uchun matn yuboring, rasm emas.")
        return
    await db.update_anime_field(data["anime_id"], "poster", message.photo[-1].file_id)
    await state.clear()
    await message.answer("✅ Yangilandi!", reply_markup=kb.admin_menu_kb())


@router.message(EditAnime.new_value)
async def edit_anime_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["field"]
    value = message.text.strip()
    if field == "year":
        if not value.isdigit():
            await message.answer("❗️ Yilni raqamda kiriting:")
            return
        value = int(value)
    if field == "poster":
        await message.answer("❗️ Iltimos, rasm yuboring.")
        return
    await db.update_anime_field(data["anime_id"], field, value)
    await state.clear()
    await message.answer("✅ Yangilandi!", reply_markup=kb.admin_menu_kb())


# =================================================================
# 🗑 O'CHIRISH
# =================================================================
@router.message(F.text == "🗑 Anime o'chirish")
async def delete_anime_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(DeleteAnime.choose_anime)
    await message.answer("🆔 O'chirmoqchi bo'lgan anime ID sini kiriting:", reply_markup=kb.cancel_kb())


@router.message(DeleteAnime.choose_anime)
async def delete_anime_choose(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗️ ID raqam bo'lishi kerak:")
        return
    anime = await db.get_anime_by_id(int(message.text.strip()))
    if not anime:
        await message.answer("❗️ Bunday ID li anime topilmadi:")
        return
    await state.clear()
    await message.answer(
        f"⚠️ <b>{anime['title']}</b> (ID: {anime['id']}) rostdan o'chirilsinmi?\n"
        f"Bu amalni ortga qaytarib bo'lmaydi, barcha qismlari ham o'chadi.",
        reply_markup=kb.confirm_delete_kb(anime["id"]),
    )


@router.callback_query(kb.ConfirmCB.filter(F.action == "delete_anime"))
async def confirm_delete_anime(callback: CallbackQuery, callback_data: kb.ConfirmCB):
    if not is_admin(callback.from_user.id):
        return
    await db.delete_anime(callback_data.id)
    await callback.message.edit_text("🗑 Anime va uning barcha qismlari o'chirildi.")
    await callback.answer()


@router.callback_query(kb.ConfirmCB.filter(F.action == "cancel"))
async def cancel_delete_anime(callback: CallbackQuery, callback_data: kb.ConfirmCB):
    await callback.message.edit_text("Bekor qilindi.")
    await callback.answer()


# =================================================================
# 📊 STATISTIKA
# =================================================================
@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    total_anime = await db.count_anime()
    total_episodes = await db.count_episodes()
    total_users = await db.get_user_count()
    top = await db.get_top_anime(5)

    text = (
        f"📊 <b>{STUDIO_NAME} — Statistika</b>\n\n"
        f"🎬 Jami animelar: <b>{total_anime}</b>\n"
        f"🎞 Jami qismlar: <b>{total_episodes}</b>\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
    )
    if top:
        text += "\n🔥 <b>Eng ko'p ko'rilgan animelar:</b>\n"
        for i, a in enumerate(top, start=1):
            text += f"{i}. {a['title']} — 👁 {a['views']}\n"

    await message.answer(text)


# =================================================================
# 📢 XABAR YUBORISH (BROADCAST)
# =================================================================
@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(Broadcast.waiting_message)
    await message.answer(
        "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring "
        "(matn, rasm, video — hammasi bo'ladi):",
        reply_markup=kb.cancel_kb(),
    )


@router.message(Broadcast.waiting_message)
async def broadcast_send(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_ids = await db.get_all_user_ids()
    await message.answer(f"⏳ {len(user_ids)} ta foydalanuvchiga yuborilmoqda...", reply_markup=kb.admin_menu_kb())

    success, failed = 0, 0
    for uid in user_ids:
        try:
            await message.copy_to(uid)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(f"✅ Yuborildi: {success} ta\n❌ Yuborilmadi: {failed} ta")


# =================================================================
# 🔐 MAJBURIY OBUNA
# =================================================================
@router.message(F.text == "🔐 Majburiy obuna")
async def obuna_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    count = await db.count_channels()
    await message.answer(
        f"🔐 <b>Majburiy obuna sozlamalari</b>\n\n"
        f"Hozir <b>{count}</b> ta kanal ulangan. Yangi foydalanuvchilar botdan "
        f"foydalanishdan oldin shu kanal(lar)ga a'zo bo'lishi shart bo'ladi.",
        reply_markup=kb.obuna_menu_kb(),
    )


@router.message(F.text == "⬅️ Admin panel")
async def back_to_admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("🛠 Admin panel:", reply_markup=kb.admin_menu_kb())


@router.message(F.text == "➕ Kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddChannel.waiting_forward)
    await message.answer(
        "📢 Kanal qo'shish uchun:\n\n"
        "1️⃣ Botni o'sha kanalga <b>admin</b> qilib qo'ying\n"
        "2️⃣ Kanaldagi istalgan postni shu yerga <b>forward</b> qiling\n\n"
        "(Kanal nomi yoki ID sini yozish shart emas — aynan forward qilingan "
        "xabarni yuboring)",
        reply_markup=kb.cancel_kb(),
    )


@router.message(AddChannel.waiting_forward)
async def add_channel_forward(message: Message, state: FSMContext):
    chat = message.forward_from_chat
    if not chat or chat.type != "channel":
        await message.answer(
            "❗️ Bu forward qilingan kanal posti emas. Kanaldan xabarni forward qiling, "
            "yoki ❌ Bekor qilish tugmasini bosing."
        )
        return

    channel_id = str(chat.id)
    title = chat.title

    if chat.username:
        invite_link = f"https://t.me/{chat.username}"
        await db.add_channel(channel_id, title, invite_link)
        await state.clear()
        await message.answer(
            f"✅ <b>{title}</b> majburiy obuna ro'yxatiga qo'shildi!",
            reply_markup=kb.obuna_menu_kb(),
        )
        return

    # Yopiq (private) kanal — taklif havolasi kerak
    await state.update_data(channel_id=channel_id, title=title)
    await state.set_state(AddChannel.waiting_invite_link)
    await message.answer(
        f"🔒 <b>{title}</b> — yopiq (private) kanal ekan.\n\n"
        f"Bunday kanallar uchun taklif havolasi (invite link) kerak bo'ladi. "
        f"Kanal sozlamalari → Havola yaratish orqali oling va shu yerga yuboring "
        f"(masalan: https://t.me/+AbCdEfGhIjK):",
        reply_markup=kb.cancel_kb(),
    )


@router.message(AddChannel.waiting_invite_link)
async def add_channel_invite_link(message: Message, state: FSMContext):
    link = message.text.strip() if message.text else ""
    if not link.startswith("https://t.me/"):
        await message.answer("❗️ Havola https://t.me/ bilan boshlanishi kerak. Qaytadan yuboring:")
        return
    data = await state.get_data()
    await db.add_channel(data["channel_id"], data["title"], link)
    await state.clear()
    await message.answer(
        f"✅ <b>{data['title']}</b> majburiy obuna ro'yxatiga qo'shildi!",
        reply_markup=kb.obuna_menu_kb(),
    )


@router.message(F.text == "📋 Kanallar ro'yxati")
async def list_channels(message: Message):
    if not is_admin(message.from_user.id):
        return
    channels = await db.get_all_channels()
    if not channels:
        await message.answer("📋 Hozircha majburiy obuna kanallari yo'q.")
        return
    await message.answer(
        f"📋 <b>Majburiy obuna kanallari</b> ({len(channels)} ta)\n\n"
        f"O'chirish uchun kerakli kanal ustiga bosing:",
        reply_markup=kb.channels_list_kb(channels),
    )


@router.callback_query(kb.ChannelCB.filter(F.action == "delete"))
async def delete_channel_cb(callback: CallbackQuery, callback_data: kb.ChannelCB):
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await db.delete_channel(callback_data.id)
    channels = await db.get_all_channels()
    if channels:
        await callback.message.edit_text(
            f"📋 <b>Majburiy obuna kanallari</b> ({len(channels)} ta)\n\n"
            f"O'chirish uchun kerakli kanal ustiga bosing:",
            reply_markup=kb.channels_list_kb(channels),
        )
    else:
        await callback.message.edit_text("📋 Hozircha majburiy obuna kanallari yo'q.")
    await callback.answer("🗑 O'chirildi")