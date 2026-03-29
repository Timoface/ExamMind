from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать собеседование")],
            [KeyboardButton(text="📊 Моя статистика")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )

def get_direction_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🐍 Python", callback_data="direction_Python")],
        [InlineKeyboardButton(text="☕ Java", callback_data="direction_Java")],
        [InlineKeyboardButton(text="🌐 JavaScript", callback_data="direction_JavaScript")],
        [InlineKeyboardButton(text="🏗 Системный дизайн", callback_data="direction_SystemDesign")],
        [InlineKeyboardButton(text="⚙️ C++", callback_data="direction_CPP")],
        [InlineKeyboardButton(text="🔷 Go", callback_data="direction_Go")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_level_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🌱 Junior", callback_data="level_Junior")],
        [InlineKeyboardButton(text="📘 Middle", callback_data="level_Middle")],
        [InlineKeyboardButton(text="👑 Senior", callback_data="level_Senior")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)