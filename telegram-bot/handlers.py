from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_main_keyboard, get_direction_keyboard, get_level_keyboard
from interview import InterviewManager


class InterviewState(StatesGroup):
    choosing_direction = State()
    choosing_level = State()
    theory_question = State()
    coding_question = State()
    soft_skills_question = State()


def register_handlers(dp: Dispatcher, interview_manager: InterviewManager):
    @dp.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "👋 Привет! Я ExamMind: Pro — твой ИИ-тренер для подготовки к IT-собеседованиям.\n\n"
            "Я помогу прокачать теорию, алгоритмы и soft skills.\n"
            "Готов начать? Нажми кнопку ниже 👇",
            reply_markup=get_main_keyboard()
        )

    @dp.message(lambda message: message.text == "🚀 Начать собеседование")
    async def start_interview(message: Message, state: FSMContext):
        await state.set_state(InterviewState.choosing_direction)
        await message.answer(
            "Выбери направление, по которому хочешь пройти собеседование:",
            reply_markup=get_direction_keyboard()
        )

    @dp.callback_query(lambda c: c.data.startswith("direction_"))
    async def choose_direction(callback: CallbackQuery, state: FSMContext):
        direction = callback.data.replace("direction_", "")
        await state.update_data(direction=direction)
        await state.set_state(InterviewState.choosing_level)
        await callback.message.edit_text(
            f"Отлично! Ты выбрал {direction}.\nТеперь выбери уровень сложности:",
            reply_markup=get_level_keyboard()
        )
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith("level_"))
    async def choose_level(callback: CallbackQuery, state: FSMContext):
        level = callback.data.replace("level_", "")
        user_data = await state.get_data()
        direction = user_data.get("direction")

        user_id = callback.from_user.id
        interview_manager.start_interview(user_id, direction, level)

        await state.update_data(level=level)
        await callback.message.edit_text(
            f"✅ Готово!\n\n"
            f"Направление: {direction}\n"
            f"Уровень: {level}\n\n"
            "Начинаем собеседование...\n"
            "Первый вопрос по теории:"
        )

        # Получаем первый теоретический вопрос
        question = interview_manager.get_next_theory_question(user_id)
        await state.set_state(InterviewState.theory_question)
        await callback.message.answer(f"📖 {question}")
        await callback.answer()

    @dp.message(InterviewState.theory_question)
    async def handle_theory_answer(message: Message, state: FSMContext):
        user_id = message.from_user.id
        answer = message.text

        score, feedback = interview_manager.evaluate_theory_answer(user_id, answer)

        await message.answer(f"📊 Оценка: {score}/10\n\n{feedback}")

        next_question = interview_manager.get_next_coding_question(user_id)
        if next_question:
            await state.set_state(InterviewState.coding_question)
            await message.answer(f"💻 Алгоритмическая задача:\n\n{next_question}\n\nНапиши решение кодом.")
        else:
            await finish_interview(message, state, user_id)

    @dp.message(InterviewState.coding_question)
    async def handle_coding_answer(message: Message, state: FSMContext):
        user_id = message.from_user.id
        code = message.text

        score, feedback = interview_manager.evaluate_code(user_id, code)

        await message.answer(f"📊 Оценка кода: {score}/10\n\n{feedback}")

        # Переходим к soft skills
        next_question = interview_manager.get_next_soft_question(user_id)
        if next_question:
            await state.set_state(InterviewState.soft_skills_question)
            await message.answer(f"🗣 Вопрос на soft skills:\n\n{next_question}")
        else:
            await finish_interview(message, state, user_id)

    @dp.message(InterviewState.soft_skills_question)
    async def handle_soft_answer(message: Message, state: FSMContext):
        user_id = message.from_user.id
        answer = message.text

        score, feedback = interview_manager.evaluate_soft_answer(user_id, answer)
        await message.answer(f"📊 Оценка: {score}/10\n\n{feedback}")

        # Завершаем собеседование
        await finish_interview(message, state, user_id)

    async def finish_interview(message: Message, state: FSMContext, user_id: int):
        report = interview_manager.get_final_report(user_id)
        await message.answer(
            f"🎉 Собеседование завершено!\n\n"
            f"📈 Итоговый отчёт:\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{report}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"Хочешь пройти ещё раз? Нажми /start",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        await message.answer(
            "📚 Команды:\n"
            "/start — начать работу\n"
            "/help — справка\n\n"
            "Во время собеседования просто отвечай на вопросы.\n"
            "Код можно отправлять обычным текстом."
        )

    @dp.message(Command("cancel"))
    async def cmd_cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("❌ Собеседование отменено. Нажми /start, чтобы начать заново.")