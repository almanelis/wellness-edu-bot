from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.config import Config
from app.data.store import get_user
from app.services.calculations import (
    calculate_calorie_goal,
    calculate_water_goal,
    parse_int,
    parse_number,
)
from app.services.weather import get_temperature
from app.states import ProfileStates
from app.ui.keyboards import GENDER_KEYBOARD, MAIN_KEYBOARD, YES_NO_KEYBOARD


router = Router()

MAX_ACTIVITY_MINUTES = 300


@router.message(Command("set_profile"))
@router.message(F.text == "Профиль")
async def set_profile(message: Message, state: FSMContext) -> None:
    await state.set_state(ProfileStates.weight)
    await message.answer("Введите ваш вес (в кг):", reply_markup=ReplyKeyboardRemove())


@router.message(ProfileStates.weight)
async def profile_weight(message: Message, state: FSMContext) -> None:
    value = parse_number(message.text)
    if value is None or value <= 0:
        await message.answer("Введите корректный вес (число больше 0):")
        return
    await state.update_data(weight=value)
    await state.set_state(ProfileStates.height)
    await message.answer("Введите ваш рост (в см):")


@router.message(ProfileStates.height)
async def profile_height(message: Message, state: FSMContext) -> None:
    value = parse_number(message.text)
    if value is None or value <= 0:
        await message.answer("Введите корректный рост (число больше 0):")
        return
    await state.update_data(height=value)
    await state.set_state(ProfileStates.age)
    await message.answer("Введите ваш возраст:")


@router.message(ProfileStates.age)
async def profile_age(message: Message, state: FSMContext) -> None:
    value = parse_int(message.text)
    if value is None:
        await message.answer("Введите корректный возраст (целое число):")
        return
    await state.update_data(age=value)
    await state.set_state(ProfileStates.gender)
    await message.answer("Укажите ваш пол (м/ж):", reply_markup=GENDER_KEYBOARD)


@router.message(ProfileStates.gender)
async def profile_gender(message: Message, state: FSMContext) -> None:
    text = message.text.strip().lower()
    if text not in ("м", "ж", "m", "f"):
        await message.answer("Пожалуйста, введите 'м' или 'ж':")
        return
    gender = "m" if text in ("м", "m") else "f"
    await state.update_data(gender=gender)
    await state.set_state(ProfileStates.activity)
    await message.answer("Сколько минут активности у вас в день?")


@router.message(ProfileStates.activity)
async def profile_activity(message: Message, state: FSMContext) -> None:
    value = parse_int(message.text)
    if value is None:
        await message.answer("Введите корректное число минут (целое):")
        return
    if value > MAX_ACTIVITY_MINUTES:
        await message.answer(
            f"Введите число от 1 до {MAX_ACTIVITY_MINUTES} минут."
        )
        return
    await state.update_data(activity=value)
    await state.set_state(ProfileStates.city)
    await message.answer("В каком городе вы находитесь?", reply_markup=ReplyKeyboardRemove())


@router.message(ProfileStates.city)
async def profile_city(message: Message, state: FSMContext) -> None:
    city = message.text.strip()
    if not city:
        await message.answer("Введите корректный город:")
        return
    await state.update_data(city=city)
    await state.set_state(ProfileStates.calorie_custom)
    await message.answer(
        "Хотите задать цель калорий вручную? (да/нет)",
        reply_markup=YES_NO_KEYBOARD,
    )


@router.message(ProfileStates.calorie_custom)
async def profile_calorie_custom(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    text = message.text.strip().lower()
    if text not in ("да", "нет"):
        await message.answer("Ответьте 'да' или 'нет':")
        return
    if text == "да":
        await state.set_state(ProfileStates.calorie_value)
        await message.answer(
            "Введите вашу цель калорий (ккал):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    await finalize_profile(message, state, config, skip_calorie_calc=False)


@router.message(ProfileStates.calorie_value)
async def profile_calorie_value(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    value = parse_int(message.text)
    if value is None:
        await message.answer("Введите корректное число калорий (целое):")
        return
    await state.update_data(calorie_goal=value)
    await finalize_profile(message, state, config, skip_calorie_calc=True)


async def finalize_profile(
    message: Message,
    state: FSMContext,
    config: Config,
    skip_calorie_calc: bool,
) -> None:
    data = await state.get_data()
    user = get_user(message.from_user.id)
    user.update(
        {
            "weight": data["weight"],
            "height": data["height"],
            "age": data["age"],
            "gender": data["gender"],
            "activity": data["activity"],
            "city": data["city"],
        }
    )

    temp = get_temperature(user["city"], config.openweather_api_key)
    user["water_goal"] = calculate_water_goal(
        user["weight"], user["activity"], temp
    )
    if not skip_calorie_calc:
        user["calorie_goal"] = calculate_calorie_goal(
            user["weight"],
            user["height"],
            user["age"],
            user["activity"],
            user["gender"],
        )
    else:
        user["calorie_goal"] = data["calorie_goal"]

    user["logged_water"] = 0
    user["logged_calories"] = 0
    user["burned_calories"] = 0
    user["extra_water_from_workouts"] = 0

    temp_text = "недоступна"
    if temp is not None:
        temp_text = f"{temp:.1f}°C"
    await message.answer(
        "Профиль сохранен!\n"
        f"Температура: {temp_text}\n"
        f"Норма воды: {user['water_goal']} мл\n"
        f"Норма калорий: {user['calorie_goal']} ккал",
        reply_markup=MAIN_KEYBOARD,
    )
    await state.clear()
