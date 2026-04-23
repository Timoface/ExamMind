from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
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
            "👋 Привет! Я ExamMind: Pro — твой ИИ-тренер.\n"
            "Я генерирую вопросы в реальном времени с помощью LLM.",
            reply_markup=get_main_keyboard()
        )

    @dp.message(lambda message: message.text == "🚀 Начать собеседование")
    async def start_interview(message: Message, state: FSMContext):
        await state.set_state(InterviewState.choosing_direction)
        await message.answer("Выбери направление:", reply_markup=get_direction_keyboard())

    @dp.callback_query(lambda c: c.data.startswith("direction_"))
    async def choose_direction(callback: CallbackQuery, state: FSMContext):
        direction = callback.data.replace("direction_", "")
        await state.update_data(direction=direction)
        await state.set_state(InterviewState.choosing_level)
        await callback.message.edit_text(f"Выбрано: {direction}. Теперь уровень:", reply_markup=get_level_keyboard())

    @dp.callback_query(lambda c: c.data.startswith("level_"))
    async def choose_level(callback: CallbackQuery, state: FSMContext):
        level = callback.data.replace("level_", "")
        user_data = await state.get_data()
        direction = user_data.get("direction")
        user_id = callback.from_user.id

        interview_manager.start_interview(user_id, direction, level)
        await state.update_data(level=level)

        sent_msg = await callback.message.edit_text("🤖 ИИ генерирует первый вопрос по теории...")

        question = await interview_manager.get_next_question(user_id, "theory")
        await state.set_state(InterviewState.theory_question)
        await sent_msg.edit_text(f"📖 Вопрос по теории:\n\n{question}")

    @dp.message(InterviewState.theory_question)
    async def handle_theory_answer(message: Message, state: FSMContext):
        user_id = message.from_user.id
        wait_msg = await message.answer("⏳ Оцениваю ваш ответ...")

        score, feedback, correct = await interview_manager.process_answer(user_id, message.text, "theory")
        await wait_msg.edit_text(f"📊 Оценка: {score}/10\n\n💡 Фидбек: {feedback}\n\n✅ Идеал: {correct}")

        next_q = await interview_manager.get_next_question(user_id, "coding")
        await state.set_state(InterviewState.coding_question)
        await message.answer(f"💻 Задача на кодинг:\n\n{next_q}")

    @dp.message(InterviewState.coding_question)
    async def handle_coding_answer(message: Message, state: FSMContext):
        user_id = message.from_user.id
        wait_msg = await message.answer("🧪 Анализирую код...")

        score, feedback, correct = await interview_manager.process_answer(user_id, message.text,
                                                                          "coding_skills")
        await wait_msg.edit_text(f"📊 Оценка кода: {score}/10\n\n{feedback}")

        next_q = await interview_manager.get_next_question(user_id, "soft_skills")
        await state.set_state(InterviewState.soft_skills_question)
        await message.answer(f"🗣 Вопрос на Soft Skills:\n\n{next_q}")

    @dp.message(InterviewState.soft_skills_question)
    async def handle_soft_answer(message: Message, state: FSMContext):
        user_id = message.from_user.id
        await interview_manager.process_answer(user_id, message.text, "soft_skills")

        report = interview_manager.get_final_report(user_id)
        await message.answer(report, reply_markup=get_main_keyboard())
        await state.clear()