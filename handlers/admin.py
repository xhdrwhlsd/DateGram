from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from states import AdminState
from keyboards import (
    admin_main_kb, admin_info_kb, admin_segment_kb, 
    admin_gender_kb, report_action_kb, admin_back_inline
)
from database import Database

db = Database()
router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    await state.clear()
    await message.answer("🛑 <b>Панель администратора</b>", reply_markup=admin_main_kb, parse_mode="HTML")

@router.callback_query(F.data == "admin_home")
async def back_home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🛑 <b>Панель администратора</b>", reply_markup=admin_main_kb, parse_mode="HTML")


@router.callback_query(F.data == "admin_reports")
async def view_reports(call: CallbackQuery):
    report = db.get_pending_report()
    if not report:
        return await call.answer("Активных жалоб нет! 🎉", show_alert=True)
    
    # Получаем инфо
    reported_user = db.get_user(report['reported_id'])
    reporter_user = db.get_user(report['reporter_id'])
    
    # Если пользователя уже нет или он удален
    if not reported_user:
        db.resolve_report(report['id'], 'dismissed') 
        return await view_reports(call)

    text = (f"⚠️ <b>Жалоба #{report['id']}</b>\n\n"
            f"📨 От: {reporter_user['name'] if reporter_user else 'Unknown'} (ID: {report['reporter_id']})\n"
            f"👤 На: {reported_user['name']}, {reported_user['age']} (ID: {report['reported_id']})\n"
            f"📝 Причина: {report['reason']}\n\n"
            f"Выберите действие:")
    
    try:
        # Если есть фото у нарушителя, показываем его
        if reported_user['photo_id']:
            await call.message.answer_photo(
                reported_user['photo_id'], 
                caption=text, 
                reply_markup=report_action_kb(report['id'], report['reported_id']), 
                parse_mode="HTML"
            )
            await call.message.delete() # Удаляем старое текстовое сообщение меню
        else:
            await call.message.edit_text(text, reply_markup=report_action_kb(report['id'], report['reported_id']), parse_mode="HTML")
    except:
        await call.message.answer("Ошибка отображения жалобы.", reply_markup=admin_main_kb)

@router.callback_query(F.data.startswith("rep_ban_"))
async def approve_ban(call: CallbackQuery, bot: Bot):
    _, _, r_id, u_id = call.data.split("_")
    db.ban_user(int(u_id))
    db.resolve_report(int(r_id), "approved")
    
    await call.answer("Пользователь забанен, жалоба закрыта.")
    try: await bot.send_message(int(u_id), "⛔️ Ваш аккаунт заблокирован администрацией за нарушение правил.")
    except: pass
    
    # Показываем следующую жалобу (рекурсия)
    await view_reports(call)

@router.callback_query(F.data.startswith("rep_dismiss_"))
async def dismiss_report(call: CallbackQuery):
    r_id = int(call.data.split("_")[2])
    db.resolve_report(r_id, "dismissed")
    await call.answer("Жалоба отклонена.")
    await view_reports(call)



@router.callback_query(F.data == "admin_edit_info")
async def info_menu(call: CallbackQuery):
    await call.message.edit_text("Выберите раздел для редактирования:", reply_markup=admin_info_kb)

TEXT_KEYS = {
    "edit_text_rules": ("rules", AdminState.edit_rules, "📜 Введите текст Правил:"),
    "edit_text_faq": ("faq", AdminState.edit_faq, "❓ Введите текст FAQ:"),
    "edit_text_support": ("support", AdminState.edit_support, "👨‍💻 Введите контакт поддержки (например @username):")
}

@router.callback_query(F.data.in_(TEXT_KEYS.keys()))
async def start_edit_text(call: CallbackQuery, state: FSMContext):
    key, state_obj, prompt = TEXT_KEYS[call.data]
    await state.update_data(text_key=key)
    await call.message.edit_text(prompt, reply_markup=admin_back_inline)
    await state.set_state(state_obj)

@router.message(AdminState.edit_rules)
@router.message(AdminState.edit_faq)
@router.message(AdminState.edit_support)
async def save_admin_text(message: Message, state: FSMContext):
    data = await state.get_data()
    db.set_text(data['text_key'], message.text)
    await message.answer("✅ Информация обновлена!", reply_markup=admin_info_kb)
    await state.clear()



#РАССЫЛКА


#ОБЩАЯ
@router.callback_query(F.data == "admin_broadcast_all")
async def broadcast_all_start(call: CallbackQuery, state: FSMContext):
    await state.update_data(segment_type='all', segment_value=None)
    await call.message.edit_text("📢 Введите текст (или фото+текст) для рассылки ВСЕМ пользователям:", reply_markup=admin_back_inline)
    await state.set_state(AdminState.broadcast_text)

#СЕГМЕНТИРОВАННАЯ Рассылка
@router.callback_query(F.data == "admin_broadcast_segment")
async def broadcast_seg_menu(call: CallbackQuery):
    await call.message.edit_text("🎯 Выберите критерий сегментации:", reply_markup=admin_segment_kb)

#ВЫБОР ПОЛА 
@router.callback_query(F.data == "seg_gender")
async def ask_gender(call: CallbackQuery):
    await call.message.edit_text("Выберите пол:", reply_markup=admin_gender_kb)

@router.callback_query(F.data.startswith("val_gender_"))
async def set_gender(call: CallbackQuery, state: FSMContext):
    g_val = call.data.split("_")[2] # male / female
    await state.update_data(segment_type='gender', segment_value=g_val)
    target = "Парням" if g_val == "male" else "Девушкам"
    await call.message.edit_text(f"📢 Введите текст рассылки для: {target}", reply_markup=admin_back_inline)
    await state.set_state(AdminState.broadcast_text)

# ВЫБОР ГОРОДА 
@router.callback_query(F.data == "seg_city")
async def ask_city(call: CallbackQuery, state: FSMContext):
    await state.update_data(segment_type='city')
    await call.message.edit_text("🏙 Введите название города (или его часть):", reply_markup=admin_back_inline)
    await state.set_state(AdminState.segment_value)

# ВЫБОР ВОЗРАСТА 
@router.callback_query(F.data == "seg_age")
async def ask_age(call: CallbackQuery, state: FSMContext):
    await state.update_data(segment_type='age')
    await call.message.edit_text("🔞 Введите диапазон возраста (например: 18-25) или одно число:", reply_markup=admin_back_inline)
    await state.set_state(AdminState.segment_value)

# ОБРАБОТКА ЗНАЧЕНИЯ (ВОЗРАСТ/ГОРОД) 
@router.message(AdminState.segment_value)
async def process_segment_value(message: Message, state: FSMContext):
    data = await state.get_data()
    seg_type = data['segment_type']
    
    final_value = None
    
    if seg_type == 'age':
        try:
            if '-' in message.text:
                parts = message.text.split('-')
                final_value = (int(parts[0]), int(parts[1]))
            else:
                val = int(message.text)
                final_value = (val, val)
        except:
            return await message.answer("❌ Неверный формат. Примеры: 18-25 или 20. Попробуйте еще раз.", reply_markup=admin_back_inline)
    
    elif seg_type == 'city':
        final_value = message.text.strip()
        
    await state.update_data(segment_value=final_value)
    await message.answer(f"✅ Фильтр принят. Теперь введите текст рассылки:", reply_markup=admin_back_inline)
    await state.set_state(AdminState.broadcast_text)


@router.message(AdminState.broadcast_text)
async def perform_broadcast(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    seg_type = data.get('segment_type', 'all')
    seg_val = data.get('segment_value')
    
    if seg_type == 'all':
        users_ids = db.get_all_users()
    else:
        users_ids = db.get_users_by_criteria(seg_type, seg_val)
    
    if not users_ids:
        await message.answer("⚠️ Пользователей по такому критерию не найдено.", reply_markup=admin_main_kb)
        return await state.clear()
    
    await message.answer(f"🚀 Начинаю рассылку на {len(users_ids)} пользователей...")
    
    count = 0
    for uid in users_ids:
        try:
            if message.photo:
                await bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "", parse_mode="HTML")
            else:
                await bot.send_message(uid, message.text, parse_mode="HTML")
            count += 1
        except: pass
            
    await message.answer(f"✅ Рассылка завершена. Успешно доставлено: {count}", reply_markup=admin_main_kb)
    await state.clear()