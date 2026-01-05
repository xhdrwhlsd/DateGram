from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- Пользовательские клавиатуры ---

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📂Моя анкета"), KeyboardButton(text="🔎Искать"), KeyboardButton(text="❤️Новые лайки")],
    [KeyboardButton(text="ℹ️О боте"), KeyboardButton(text="🤵Реферальная система"), KeyboardButton(text="💞Мэтчи")]
], resize_keyboard=True)

back_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True)

def my_profile_kb(is_active):
    vis_text = "🚫Отключить анкету" if is_active else "✅Включить анкету"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔄Изменить полностью"), KeyboardButton(text="📝Описание"), KeyboardButton(text="📷Фото")],
        [KeyboardButton(text="🎵Музыку"), KeyboardButton(text="✨Интересы"), KeyboardButton(text="🏙Город")],
        [KeyboardButton(text="🧐Искомый типаж"), KeyboardButton(text="👱Мой типаж"), KeyboardButton(text=vis_text)],
        [KeyboardButton(text="Назад")]
    ], resize_keyboard=True)

def type_selection_kb(page, total_pages=3):
    start_num = page * 9 + 1
    end_num = start_num + 9
    buttons = []
    row = []
    for i in range(start_num, end_num):
        if i > 27: break
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"sel_type_{i}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"type_page_{page-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="dummy"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"type_page_{page+1}"))
    buttons.append(nav_row)
    
    buttons.append([InlineKeyboardButton(text="0 - Пропустить", callback_data="sel_type_0")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def search_kb(target_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️", callback_data=f"like_{target_id}"), InlineKeyboardButton(text="👎", callback_data=f"dislike_{target_id}"), InlineKeyboardButton(text="✉️", callback_data=f"msg_{target_id}")],
        [InlineKeyboardButton(text="🔙", callback_data="prev"), InlineKeyboardButton(text="❗Жалоба", callback_data=f"report_{target_id}")]
    ])

def incoming_likes_kb(target_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Взаимно", callback_data=f"accept_{target_id}"), InlineKeyboardButton(text="👎 Скрыть", callback_data=f"decline_{target_id}")]
    ])

def matches_nav_kb(index, total):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data=f"m_prev_{index}"), InlineKeyboardButton(text=f"{index+1}/{total}", callback_data="none"), InlineKeyboardButton(text="➡️", callback_data=f"m_next_{index}")]
    ])

# --- Клавиатуры регистрации ---
def reg_cancel_kb(is_edit=False):
    if is_edit: return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отмена")]], resize_keyboard=True)
    return None

def gender_kb(is_edit=False):
    btns = [[KeyboardButton(text="Парень"), KeyboardButton(text="Девушка")]]
    if is_edit: btns.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)

# Кнопки Да/Нет
confirm_disable_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]], resize_keyboard=True)
yes_no_kb = confirm_disable_kb # Алиас для совместимости

about_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📜Правила", callback_data="rules"), InlineKeyboardButton(text="📔FAQ", callback_data="faq"), InlineKeyboardButton(text="📓Обратная связь", callback_data="support")]
])

# --- АДМИН ПАНЕЛЬ ---
admin_main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚠️ Новые жалобы", callback_data="admin_reports")],
    [InlineKeyboardButton(text="ℹ️ Изменить информацию", callback_data="admin_edit_info")],
    [InlineKeyboardButton(text="📢 Сообщение всем", callback_data="admin_broadcast_all")],
    [InlineKeyboardButton(text="🎯 Сегментированная рассылка", callback_data="admin_broadcast_segment")]
])

admin_info_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📜 Правила", callback_data="edit_text_rules")],
    [InlineKeyboardButton(text="❓ FAQ", callback_data="edit_text_faq")],
    [InlineKeyboardButton(text="👨‍💻 Аккаунт поддержки", callback_data="edit_text_support")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_home")]
])

admin_segment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚹🚺 Настройка по полу", callback_data="seg_gender")],
    [InlineKeyboardButton(text="🔞 Настройка по возрасту", callback_data="seg_age")],
    [InlineKeyboardButton(text="🏙 Настройка по региону", callback_data="seg_city")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_home")]
])

admin_gender_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Парни", callback_data="val_gender_male"), InlineKeyboardButton(text="Девушки", callback_data="val_gender_female")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_broadcast_segment")]
])

admin_back_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Отмена", callback_data="admin_home")]])

def report_action_kb(report_id, user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить (Бан)", callback_data=f"rep_ban_{report_id}_{user_id}")],
        [InlineKeyboardButton(text="❌ Отказать", callback_data=f"rep_dismiss_{report_id}")],
        [InlineKeyboardButton(text="⬅️ Выход", callback_data="admin_home")]
    ])