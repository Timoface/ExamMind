import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers import register_handlers
from interview import InterviewManager

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

interview_manager = InterviewManager()

register_handlers(dp, interview_manager)

async def main():
    logging.info("Бот ExamMind: Pro запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
