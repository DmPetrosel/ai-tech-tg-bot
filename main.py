# main.py
import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.models import async_main


async def main():
    await async_main()
    bot = Bot(token='7577583878:AAFWQC71OXuwadRJPqt4r6puc2m6MNlMok8') 
    dp = Dispatcher()
    dp.include_router(router)
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')