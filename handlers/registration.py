from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import Reg
from keyboards import main_menu, gender_kb, reg_cancel_kb, type_selection_kb
from database import Database

db = Database()
router = Router()

STICKERS_FEMALE = [
    "CAACAgIAAxkBAAICiGlNxrh9qiIpai385k04gII_kPtHAAKUdwAC4GipS17kJGjO773uNgQ",
    "CAACAgIAAxkBAAICimlNxrn2Z7Jbpfd7Le2NzFvcuW1xAALBcwAC6W6pS3jVt00lTcQaNgQ",
    "CAACAgIAAxkBAAICjGlNxro8ZHzV3PYcdT0sroBp9NjKAAKycAACFFepS2QZfumCGonINgQ",
    "CAACAgIAAxkBAAICjmlNxrqTV7lgsJdlwLbXz8cKgoSCAAIFbwAC7vyoS3ZzUVbNNjNSNgQ",
    "CAACAgIAAxkBAAICkGlNxrvzMYxYr489x0b9eTc6FXpjAAL7aQACt5apS1jjMGND_zKyNgQ",
    "CAACAgIAAxkBAAICkmlNxrxtFgtOEz_41BLBhkJd00yQAALtbwACrLWwS01_XXMjD_VHNgQ"
]

STICKERS_MALE = [
    "CAACAgIAAxkBAAICeGlNxpKd7ZEzMbWwU9Zt1prGUFHIAAIFbAACwBuoSwoYDmCaTBZRNgQ",
    "CAACAgIAAxkBAAICemlNxpPrAAF-NmOgOauAAAHD9l_PUYUAAvN6AAJKzrBLQdGYFcg_IWs2BA",
    "CAACAgIAAxkBAAICfGlNxpQLY-YaBF--bKK4M_g3s8hwAAJYeQACwhapSzlz9qah0VuLNgQ",
    "CAACAgIAAxkBAAICfmlNxpW-oAL17lxS7c8vJlOfcTwbAAIffQACRMmoSxJ0H-iRk89TNgQ",
    "CAACAgIAAxkBAAICgGlNxpZMN3bXYUEZ3WN6-E48ffQOAALKqQACIdewS8S46_Wi1s-6NgQ",
    "CAACAgIAAxkBAAICgmlNxpch207tHBsMucBjWpPqf6GAAALJawACyoWwSxkHNN2-m7Q-NgQ"
]

async def show_type_selector(message_obj, state: FSMContext, bot: Bot, page=0, is_new=True):
    data = await state.get_data()
    mode = data.get('type_mode', 'target')
    gender_key = data.get('target_gender', 'male') if mode == 'target' else data.get('gender', 'male')
    stickers_list = STICKERS_MALE if gender_key == 'male' else STICKERS_FEMALE

    idx_start = page * 2
    idx_end = idx_start + 2
    current_stickers = stickers_list[idx_start:idx_end]

    if not is_new:
        for mid in data.get('msgs_to_del', []):
            try: await bot.delete_message(chat_id=message_obj.chat.id, message_id=mid)
            except: pass
            
    new_msgs = []
    for sticker_id in current_stickers:
        m = await bot.send_sticker(chat_id=message_obj.chat.id, sticker=sticker_id)
        new_msgs.append(m.message_id)

    text = "Выбери номер типажа (см. на стикерах):"
    kb = type_selection_kb(page, total_pages=3)

    m_menu = await bot.send_message(chat_id=message_obj.chat.id, text=text, reply_markup=kb)
    new_msgs.append(m_menu.message_id)

    await state.update_data(msgs_to_del=new_msgs)

@router.message(F.text == "❌ Отмена")
async def cancel_reg(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu)

async def start_reg(message: Message, state: FSMContext):
    data = await state.get_data()
    is_edit = data.get("is_edit", False)
    kb = reg_cancel_kb(is_edit) if is_edit else ReplyKeyboardRemove()
    await message.answer("Приветствую в Dategram! Для начала укажи свой возраст.", reply_markup=kb)
    await state.set_state(Reg.age)

@router.message(Reg.age)
async def get_age(message: Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("Введите число.")
    await state.update_data(age=int(message.text))

    data = await state.get_data()
    is_edit = data.get("is_edit", False)
    await message.answer("Теперь определимся с полом.", reply_markup=gender_kb(is_edit))
    await state.set_state(Reg.gender)

@router.message(Reg.gender)
async def get_gender(message: Message, state: FSMContext):
    if message.text not in ["Парень", "Девушка"]:
        return await message.answer("Выберите кнопку.")

    my_gender = "male" if message.text == "Парень" else "female"
    await state.update_data(gender=my_gender)
    target_gender = "female" if my_gender == "male" else "male"
    await state.update_data(target_gender=target_gender)

    await message.answer("Из какого ты города?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.city)

@router.message(Reg.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    is_edit = data.get("is_edit", False)
    kb = reg_cancel_kb(is_edit) if is_edit else ReplyKeyboardRemove()
    await message.answer("Как тебя зовут?", reply_markup=kb)
    await state.set_state(Reg.name)

@router.message(Reg.name)
async def get_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=message.text)
    await state.update_data(type_mode='target')
    await message.answer("Выбери искомый типаж:", reply_markup=ReplyKeyboardRemove())
    await show_type_selector(message, state, bot, page=0, is_new=True)
    await state.set_state(Reg.target_type)

@router.callback_query(F.data.startswith("type_page_"))
async def nav_types(call: CallbackQuery, state: FSMContext, bot: Bot):
    page = int(call.data.split("_")[2])
    await show_type_selector(call.message, state, bot, page=page, is_new=False)
    await call.answer()

@router.callback_query(F.data.startswith("sel_type_"))
async def select_type(call: CallbackQuery, state: FSMContext, bot: Bot):
    num = int(call.data.split("_")[2])
    data = await state.get_data()
    mode = data.get('type_mode')

    for mid in data.get('msgs_to_del', []):
        try: await bot.delete_message(chat_id=call.message.chat.id, message_id=mid)
        except: pass

    if mode == 'target':
        await state.update_data(target_type=str(num))
        await state.update_data(type_mode='my')
        await call.message.answer("Теперь выбери, с каким типажом соотносишь себя:")
        await show_type_selector(call.message, state, bot, page=0, is_new=True)
        await state.set_state(Reg.my_type)
        
    elif mode == 'my':
        await state.update_data(my_type=str(num))
        is_edit = data.get("is_edit", False)
        kb = reg_cancel_kb(is_edit) if is_edit else ReplyKeyboardRemove()
        await call.message.answer("Расскажи немного о себе (Био)", reply_markup=kb)
        await state.set_state(Reg.bio)

    await call.answer()

@router.message(Reg.bio)
async def get_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    data = await state.get_data()
    is_edit = data.get("is_edit", False)
    kb = reg_cancel_kb(is_edit) if is_edit else ReplyKeyboardRemove()
    await message.answer("Пришли свое фото для анкеты:", reply_markup=kb)
    await state.set_state(Reg.photo)

@router.message(Reg.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    
    # Очищаем временные поля
    if 'is_edit' in data: del data['is_edit']
    if 'msgs_to_del' in data: del data['msgs_to_del']
    if 'type_mode' in data: del data['type_mode']
        
    data.update({
        'tg_id': message.from_user.id, 
        'username': message.from_user.username,
        'photo': photo_id,
        'music_file_id': None,
        'interests': None
    })

    db.add_user(data)
    await state.clear()
    await message.answer("Анкета готова! Добро пожаловать.", reply_markup=main_menu)

@router.message(Reg.photo)
async def not_a_photo(message: Message):
    await message.answer("Пожалуйста, отправь фото.")