from aiogram.fsm.state import State, StatesGroup

class Reg(StatesGroup):
    age = State()
    gender = State()
    city = State()
    name = State()
    target_type = State()
    my_type = State()
    bio = State()
    photo = State()

class SearchState(StatesGroup):
    writing_message = State()
    writing_report = State()

class EditProfile(StatesGroup):
    waiting_for_value = State()

class AdminState(StatesGroup):
    broadcast_text = State()     # Текст для любой рассылки
    
    # Сегментация
    segment_value = State()      # Значение критерия (М, 18-20, Москва)
    
    # Редактирование инфо
    edit_rules = State()
    edit_faq = State()
    edit_support = State()