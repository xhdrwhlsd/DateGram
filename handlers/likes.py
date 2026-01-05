from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from keyboards import incoming_likes_kb, back_kb, main_menu
from database import Database

db = Database()
router = Router()

async def render_like(message: Message, user_id):
    likes = db.get_incoming_likes(user_id)
    if not likes:
        return await message.answer("Новых лайков нет.", reply_markup=main_menu)

    target = likes[0]

    caption = f"Вас лайкнул:\n{target['name']}, {target['age']}, {target['city']}"
    if target['msg_content']: 
        caption += f"\n✉️: {target['msg_content']}"

    await message.answer_photo(
        target['photo_id'], 
        caption=caption, 
        reply_markup=incoming_likes_kb(target['tg_id'])
    )

    if target['music_file_id']: 
        await message.answer_audio(target['music_file_id'])

@router.message(F.text == "❤️Новые лайки")
async def start_likes(message: Message):
    await message.answer("Вам поставили лайк:", reply_markup=back_kb)
    await render_like(message, message.from_user.id)

@router.callback_query(F.data.startswith("accept_"))
async def accept_like(call: CallbackQuery, bot: Bot):
    target_id = int(call.data.split("_")[1])

    db.add_reaction(call.from_user.id, target_id, "like")

    try: 
        await bot.send_message(
            target_id, 
            "🎉 <b>Мэтч!</b> Пользователь ответил вам взаимностью!\nЗагляните в раздел «💞Мэтчи»",
            parse_mode="HTML"
        )
    except: 
        pass

    await call.answer("Мэтч!")
    await call.message.delete()
    await render_like(call.message, call.from_user.id)

@router.callback_query(F.data.startswith("decline_"))
async def decline_like(call: CallbackQuery):
    target_id = int(call.data.split("_")[1])
    db.add_reaction(call.from_user.id, target_id, "dislike")

    await call.answer("Скрыто")
    await call.message.delete()
    await render_like(call.message, call.from_user.id)