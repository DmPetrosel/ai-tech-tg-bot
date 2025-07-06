# main.py
import asyncio
from aiogram import Bot, Dispatcher
from loguru import logger
from app.handlers import router
from app.database.models import async_main
from configparser import ConfigParser

from app.utils import setup_logger


config = ConfigParser()
config.read("config.ini")
setup_logger()


async def main():
    await async_main()
    bot = Bot(token=config.get("bot", "token"))
    dp = Dispatcher(bot=bot)
    dp.include_router(router)

    try:
        logger.info("starting bot")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
