from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from keyboards import main_menu
from database import Database
from handlers.registration import start_reg

db = Database()
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    user = db.get_user(message.from_user.id)

    if user:
        if user['is_banned']: return await message.answer("⛔️ Вы заблокированы.")
        await message.answer(f"С возвращением, {user['name']}!", reply_markup=main_menu)
    else:
        # Рефералка
        ref_id = None
        if command.args and command.args.isdigit():
            rid = int(command.args)
            if rid != message.from_user.id: ref_id = rid
        
        await state.update_data(referral_id=ref_id)
        await start_reg(message, state)