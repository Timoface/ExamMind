import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from handlers import register_handlers
from interview import InterviewManager

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(proxy='http://20.204.228.118:8080')
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

interview_manager = InterviewManager()

register_handlers(dp, interview_manager)

async def main():
    logging.info(f"Бот ExamMind: Pro запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
