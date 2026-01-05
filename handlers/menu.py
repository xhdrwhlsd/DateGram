from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import about_kb, back_kb
from database import Database
from config import BOT_USERNAME

db = Database()
router = Router()

@router.message(F.text == "ℹ️О боте")
async def about(message: Message):
    await message.answer("Инфо:", reply_markup=about_kb)
    await message.answer("Назад", reply_markup=back_kb)

@router.callback_query(F.data == "rules")
async def rules(call: CallbackQuery):
    await call.message.answer(db.get_text("rules"))
    await call.answer()

@router.callback_query(F.data == "faq")
async def faq(call: CallbackQuery):
    await call.message.answer(db.get_text("faq"))
    await call.answer()

@router.callback_query(F.data == "support")
async def sup(call: CallbackQuery):
    # Теперь берем текст из базы (который админ редактировал в 'Изменить информацию')
    contact = db.get_text("support")
    if contact == "Текст не задан.":
        text = "Поддержка: Пишите администратору."
    else:
        text = f"📬 По вопросам и предложениям пишите: {contact}"
    
    await call.message.answer(text)
    await call.answer()

@router.message(F.text == "🤵Реферальная система")
async def ref(message: Message):
    u = db.get_user(message.from_user.id)
    link = f"https://t.me/{BOT_USERNAME}?start={message.from_user.id}"
    await message.answer(f"Приглашено: {u['referral_count']}\nТвоя ссылка:\n{link}", reply_markup=back_kb)