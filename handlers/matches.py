from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import matches_nav_kb, back_kb, main_menu
from database import Database

db = Database()
router = Router()

async def render_match(message: Message, user_id, idx, edit=False):
    matches = db.get_matches(user_id)
    if not matches:
        if edit: return
        return await message.answer("Мэтчей пока нет.", reply_markup=main_menu)

    if idx >= len(matches): idx = 0
    if idx < 0: idx = len(matches) - 1

    m = matches[idx]
    cap = f"{m['name']}, {m['age']}\n@{m['username']}"

    if edit:
        await message.delete()
        await message.answer_photo(m['photo_id'], caption=cap, reply_markup=matches_nav_kb(idx, len(matches)))
    else:
        await message.answer_photo(m['photo_id'], caption=cap, reply_markup=matches_nav_kb(idx, len(matches)))

@router.message(F.text == "💞Мэтчи")
async def show_matches(message: Message):
    await message.answer("Твои пары:", reply_markup=back_kb)
    await render_match(message, message.from_user.id, 0)

@router.callback_query(F.data.startswith("m_"))
async def nav_matches(call: CallbackQuery):
    action, idx = call.data.split("_")[1], int(call.data.split("_")[2])
    new_idx = idx + 1 if action == "next" else idx - 1
    await render_match(call.message, call.from_user.id, new_idx, edit=True)
    await call.answer()