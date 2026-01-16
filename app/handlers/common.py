from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from app.ui.keyboards import MAIN_KEYBOARD


router = Router()


@router.message(CommandStart())
@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Я помогу рассчитать нормы воды и калорий.\n"
        "Команды:\n"
        "Профиль — настройка профиля\n"
        "Вода — записать воду\n"
        "Еда — записать еду\n"
        "Тренировка — записать тренировку\n"
        "Прогресс — текущий статус\n"
        "Помощь — справка",
        reply_markup=MAIN_KEYBOARD,
    )
