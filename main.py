import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from config import TOKEN
from handlers import start, registration, menu, profile, search, likes, matches, admin

async def main():
    logging.basicConfig(level=logging.INFO)

    session = AiohttpSession(proxy="http://proxy.server:3128") # Если нужен прокси
    bot = Bot(token=TOKEN, session=session)

    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(registration.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(search.router)
    dp.include_router(likes.router)
    dp.include_router(matches.router)
    dp.include_router(start.router)

    print("Dategram Bot Full Version Started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")