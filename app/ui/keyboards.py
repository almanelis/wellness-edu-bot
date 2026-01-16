from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профиль"), KeyboardButton(text="Прогресс")],
        [KeyboardButton(text="Вода"), KeyboardButton(text="Еда")],
        [KeyboardButton(text="Тренировка"), KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True,
)

YES_NO_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="да"), KeyboardButton(text="нет")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

GENDER_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="м"), KeyboardButton(text="ж")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)
