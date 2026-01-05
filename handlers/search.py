from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import SearchState
from keyboards import search_kb, back_kb, main_menu
from database import Database

db = Database()
router = Router()
PLACEHOLDER_URL = "https://placehold.co/300x200.png?text=User+Photo"

async def render_card(message: Message, user_id):
    target = db.search_users(user_id)
    if not target: return await message.answer("Анкеты закончились.", reply_markup=main_menu)

    ints = f"\n✨ {target['interests']}" if target['interests'] else ""
    caption = (f"<b>{target['name']}, {target['age']}, {target['city']}</b>\n"
               f"{target['bio']}{ints}")

    photo = target['photo_id'] if target['photo_id'] else PLACEHOLDER_URL

    await message.answer_photo(photo, caption=caption, parse_mode="HTML")

    if target['music_file_id']:
        await message.answer_audio(target['music_file_id'], caption="🎧 Любимый трек")

    await message.answer("Действия:", reply_markup=search_kb(target['tg_id']))

@router.message(F.text == "🔎Искать")
async def start_search(message: Message):
    if not db.get_user(message.from_user.id): return await message.answer("Сначала заполни анкету!")
    await message.answer("Поиск...", reply_markup=back_kb)
    await render_card(message, message.from_user.id)

# --- ЛАЙК ---
@router.callback_query(F.data.startswith("like_"))
async def handle_like(call: CallbackQuery, bot: Bot):
    target_id = int(call.data.split("_")[1])
    db.add_reaction(call.from_user.id, target_id, "like")

    try:
        await bot.send_message(
            target_id, 
            "❤️ <b>Вас кто-то оценил!</b>\nНажмите кнопку «❤️Новые лайки», чтобы посмотреть.",
            parse_mode="HTML"
        )
    except: pass

    await call.answer("Лайк ❤️")
    await call.message.delete()
    await render_card(call.message, call.from_user.id)

@router.callback_query(F.data.startswith("dislike_"))
async def handle_dislike(call: CallbackQuery):
    target_id = int(call.data.split("_")[1])
    db.add_reaction(call.from_user.id, target_id, "dislike")
    await call.answer("Дизлайк")
    await call.message.delete()
    await render_card(call.message, call.from_user.id)

# --- СООБЩЕНИЕ ---
@router.callback_query(F.data.startswith("msg_"))
async def msg_start(call: CallbackQuery, state: FSMContext):
    target_id = int(call.data.split("_")[1])
    await state.update_data(target=target_id)
    await call.message.answer("Введите сообщение:", reply_markup=back_kb)
    await state.set_state(SearchState.writing_message)
    await call.answer()

@router.message(SearchState.writing_message)
async def msg_finish(message: Message, state: FSMContext, bot: Bot):
    if message.text == "Назад":
        await state.clear()
        return await message.answer("Отмена", reply_markup=main_menu)

    data = await state.get_data()
    target_id = data['target']

    db.add_reaction(message.from_user.id, target_id, "like", message.text)

    try: 
        await bot.send_message(
            target_id, 
            "💌 <b>Вам пришло сообщение-симпатия!</b>\nЗагляните в «❤️Новые лайки».",
            parse_mode="HTML"
        )
    except: pass
        
    await message.answer("Отправлено!", reply_markup=back_kb)
    await state.clear()
    await render_card(message, message.from_user.id)

# --- ЖАЛОБА ---
@router.callback_query(F.data.startswith("report_"))
async def report_start(call: CallbackQuery, state: FSMContext):
    await state.update_data(target=int(call.data.split("_")[1]))
    await call.message.answer("Причина жалобы?", reply_markup=back_kb)
    await state.set_state(SearchState.writing_report)
    await call.answer()

@router.message(SearchState.writing_report)
async def report_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    # Записываем в базу, чтобы админ увидел в разделе "Новые жалобы"
    db.add_report(message.from_user.id, data['target'], message.text)
    
    await message.answer("Жалоба отправлена модераторам.", reply_markup=back_kb)
    await state.clear()
    await render_card(message, message.from_user.id)