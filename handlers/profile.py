from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states import EditProfile
from keyboards import my_profile_kb, main_menu, confirm_disable_kb, back_kb
from database import Database
from handlers.registration import start_reg

db = Database()
router = Router()
PLACEHOLDER = "https://placehold.co/300x200.png?text=No+Photo"

@router.message(F.text == "📂Моя анкета")
async def show_profile(message: Message):
    u = db.get_user(message.from_user.id)
    if not u: return await message.answer("Анкеты нет. Введите /start")

    music_stat = "Есть" if u['music_file_id'] else "Нет"
    interests = u['interests'] if u['interests'] else "Не указаны"
    my_t = u['my_type'] if u['my_type'] != "0" else "Не указан"
    tar_t = u['target_type'] if u['target_type'] != "0" else "Любой"

    caption = (f"Вот твоя анкета:\n"
               f"{u['name']}, {u['age']}, {u['city']} - {u['bio']}\n"
               f"🎵 Музыка: {music_stat}\n"
               f"✨ Интересы: {interests}\n"
               f"👱 Я: {my_t} | 🧐 Ищу: {tar_t}")

    photo = u['photo_id'] if u['photo_id'] else PLACEHOLDER

    await message.answer_photo(photo, caption=caption)

    if u['music_file_id']:
        await message.answer_audio(u['music_file_id'], caption="Твой трек")
        
    await message.answer("Управление анкетой:", reply_markup=my_profile_kb(u['is_active']))

# --- ЛОГИКА ОТКЛЮЧЕНИЯ ---
@router.message(F.text.in_({"🚫Отключить анкету", "✅Включить анкету"}))
async def ask_toggle_status(message: Message, state: FSMContext):
    is_disabling = "🚫" in message.text
    await state.update_data(pending_status_change=is_disabling)
    text = "Вы точно хотите отключить анкету?" if is_disabling else "Вы точно хотите включить анкету?"
    await message.answer(text, reply_markup=confirm_disable_kb)

@router.message(F.text == "Да")
async def confirm_status_change(message: Message, state: FSMContext):
    data = await state.get_data()
    is_disabling = data.get('pending_status_change')
    if is_disabling is None: 
        # Если контекста нет, возможно это ответ на другой вопрос "Да"
        return await message.answer("Я вас не понял.", reply_markup=main_menu)

    new_status = 0 if is_disabling else 1
    db.update_field(message.from_user.id, "is_active", new_status)

    result_text = "Ваша анкета успешно отключена!" if is_disabling else "Ваша анкета успешно включена!"
    await message.answer(result_text, reply_markup=my_profile_kb(new_status))
    await state.update_data(pending_status_change=None)

@router.message(F.text == "Нет")
async def cancel_status_change(message: Message):
    u = db.get_user(message.from_user.id)
    if u:
        await message.answer("Действие отменено.", reply_markup=my_profile_kb(u['is_active']))
    else:
        await message.answer("Главное меню", reply_markup=main_menu)

@router.message(F.text == "Назад")
async def back_to_main(message: Message):
    await message.answer("Главное меню", reply_markup=main_menu)

@router.message(F.text == "🔄Изменить полностью")
async def re_register_btn(message: Message, state: FSMContext):
    await state.update_data(is_edit=True)
    await message.answer("Заполняем анкету заново...", reply_markup=ReplyKeyboardRemove())
    await start_reg(message, state)

# --- РЕДАКТИРОВАНИЕ ПОЛЕЙ ---
FIELD_MAP = {
    "📝Описание": "bio",
    "📷Фото": "photo",
    "🎵Музыку": "music",
    "✨Интересы": "interests",
    "🏙Город": "city",
    "🧐Искомый типаж": "target_type",
    "👱Мой типаж": "my_type"
}

@router.message(F.text.in_(FIELD_MAP.keys()))
async def edit_field_btn(message: Message, state: FSMContext):
    field = FIELD_MAP[message.text]
    await state.update_data(field=field)

    text = "Введите новое значение:"
    if field == "music": text = "Пришлите новый трек (@TgSoundBot):"
    elif field == "photo": text = "Пришлите новое фото:"
    elif "type" in field: text = "Введите номер типажа (0-27). 0 - Не важно/Не указано."

    await message.answer(text, reply_markup=back_kb)
    await state.set_state(EditProfile.waiting_for_value)

@router.message(EditProfile.waiting_for_value)
async def save_field(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.clear()
        return await show_profile(message)

    data = await state.get_data()
    field = data.get('field')
    if not field: return await state.clear()

    if field == "music":
        if message.audio: db.update_field(message.from_user.id, "music_file_id", message.audio.file_id)
        else: return await message.answer("Это не аудиофайл.")
    elif field == "photo":
        if message.photo: db.update_field(message.from_user.id, "photo_id", message.photo[-1].file_id)
        else: return await message.answer("Это не фото.")
    elif "type" in field:
        if not message.text.isdigit() or not (0 <= int(message.text) <= 27):
            return await message.answer("Пожалуйста, введите число от 0 до 27.")
        db.update_field(message.from_user.id, field, message.text)
    else:
        db.update_field(message.from_user.id, field, message.text)
        
    await message.answer("Сохранено!", reply_markup=main_menu)
    await state.clear()
    await show_profile(message)