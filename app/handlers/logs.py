from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.data.store import get_user, has_profile
from app.services.calculations import parse_int, parse_number
from app.services.food import get_food_info
from app.services.workouts import extra_water_for_minutes, workout_rate_per_min
from app.states import FoodStates, WaterStates, WorkoutStates
from app.ui.keyboards import MAIN_KEYBOARD


router = Router()


def extract_args(message: Message) -> list[str]:
    if not message.text:
        return []
    parts = message.text.split()
    return parts[1:] if len(parts) > 1 else []


@router.message(Command("log_water"))
@router.message(F.text == "Вода")
async def log_water(message: Message, state: FSMContext) -> None:
    user = get_user(message.from_user.id)
    if not has_profile(user):
        await message.answer("Сначала настройте профиль через /set_profile.")
        return
    args = extract_args(message)
    if not args:
        await state.set_state(WaterStates.amount)
        await message.answer("Сколько мл воды вы выпили?")
        return
    value = parse_int(args[0])
    if value is None:
        await message.answer("Введите корректное количество воды в мл.")
        return
    user["logged_water"] += value
    goal = user["water_goal"] + user["extra_water_from_workouts"]
    remaining = max(goal - user["logged_water"], 0)
    await message.answer(
        f"Записано {value} мл. Осталось до нормы: {remaining} мл."
    )


@router.message(WaterStates.amount)
async def log_water_amount(message: Message, state: FSMContext) -> None:
    value = parse_int(message.text)
    if value is None:
        await message.answer("Введите корректное количество воды в мл.")
        return
    user = get_user(message.from_user.id)
    user["logged_water"] += value
    goal = user["water_goal"] + user["extra_water_from_workouts"]
    remaining = max(goal - user["logged_water"], 0)
    await message.answer(
        f"Записано {value} мл. Осталось до нормы: {remaining} мл.",
        reply_markup=MAIN_KEYBOARD,
    )
    await state.clear()


@router.message(Command("log_food"))
@router.message(F.text == "Еда")
async def log_food_start(message: Message, state: FSMContext) -> None:
    user = get_user(message.from_user.id)
    if not has_profile(user):
        await message.answer("Сначала настройте профиль через /set_profile.")
        return

    args = extract_args(message)
    if args:
        query = " ".join(args).strip()
        info = get_food_info(query)
        if not info:
            await message.answer("Не нашел продукт. Попробуйте другое название.")
            return
        user["pending_food"] = info
        await state.set_state(FoodStates.grams)
        await message.answer(
            f"🍎 {info['name']} — {info['calories']} ккал на 100 г. "
            "Сколько грамм вы съели?"
        )
        return

    await state.set_state(FoodStates.query)
    await message.answer("Введите название продукта:")


@router.message(FoodStates.query)
async def log_food_query(message: Message, state: FSMContext) -> None:
    query = message.text.strip()
    if not query:
        await message.answer("Введите корректное название продукта:")
        return
    info = get_food_info(query)
    if not info:
        await message.answer("Не нашел продукт. Попробуйте другое название.")
        await state.clear()
        return
    user = get_user(message.from_user.id)
    user["pending_food"] = info
    await state.set_state(FoodStates.grams)
    await message.answer(
        f"🍎 {info['name']} — {info['calories']} ккал на 100 г. "
        "Сколько грамм вы съели?"
    )


@router.message(FoodStates.grams)
async def log_food_grams(message: Message, state: FSMContext) -> None:
    grams = parse_number(message.text)
    if grams is None or grams <= 0:
        await message.answer("Введите корректное количество грамм:")
        return
    user = get_user(message.from_user.id)
    info = user.get("pending_food")
    if not info:
        await message.answer("Не удалось найти продукт. Повторите /log_food.")
        await state.clear()
        return
    calories = float(info["calories"]) * grams / 100
    user["logged_calories"] += calories
    user["pending_food"] = None
    await message.answer(
        f"Записано: {calories:.1f} ккал.",
        reply_markup=MAIN_KEYBOARD,
    )
    await state.clear()


@router.message(Command("log_workout"))
@router.message(F.text == "Тренировка")
async def log_workout(message: Message, state: FSMContext) -> None:
    user = get_user(message.from_user.id)
    if not has_profile(user):
        await message.answer("Сначала настройте профиль через /set_profile.")
        return
    args = extract_args(message)
    if len(args) < 2:
        await state.set_state(WorkoutStates.workout_type)
        await message.answer("Введите тип тренировки (например, бег):")
        return
    minutes = parse_int(args[-1])
    if minutes is None:
        await message.answer("Введите корректное количество минут (целое):")
        return
    workout_type = " ".join(args[:-1])
    rate = workout_rate_per_min(workout_type)
    calories = rate * minutes
    user["burned_calories"] += calories

    extra_water = extra_water_for_minutes(minutes)
    user["extra_water_from_workouts"] += extra_water
    await message.answer(
        f"🏋️ {workout_type} {minutes} минут — {calories} ккал. "
        f"Дополнительно: выпейте {extra_water} мл воды."
    )


@router.message(WorkoutStates.workout_type)
async def workout_type(message: Message, state: FSMContext) -> None:
    workout_type = message.text.strip()
    if not workout_type:
        await message.answer("Введите корректный тип тренировки:")
        return
    await state.update_data(workout_type=workout_type)
    await state.set_state(WorkoutStates.minutes)
    await message.answer("Введите длительность (в минутах):")


@router.message(WorkoutStates.minutes)
async def workout_minutes(message: Message, state: FSMContext) -> None:
    minutes = parse_int(message.text)
    if minutes is None:
        await message.answer("Введите корректное количество минут (целое):")
        return
    data = await state.get_data()
    workout_type = data["workout_type"]
    user = get_user(message.from_user.id)
    rate = workout_rate_per_min(workout_type)
    calories = rate * minutes
    user["burned_calories"] += calories

    extra_water = extra_water_for_minutes(minutes)
    user["extra_water_from_workouts"] += extra_water
    await message.answer(
        f"🏋️ {workout_type} {minutes} минут — {calories} ккал. "
        f"Дополнительно: выпейте {extra_water} мл воды.",
        reply_markup=MAIN_KEYBOARD,
    )
    await state.clear()


@router.message(Command("check_progress"))
@router.message(F.text == "Прогресс")
async def check_progress(message: Message) -> None:
    user = get_user(message.from_user.id)
    if not has_profile(user):
        await message.answer("Сначала настройте профиль через /set_profile.")
        return
    water_goal = user["water_goal"] + user["extra_water_from_workouts"]
    water_remaining = max(water_goal - user["logged_water"], 0)
    net_calories = user["logged_calories"] - user["burned_calories"]
    calorie_remaining = max(user["calorie_goal"] - net_calories, 0)

    await message.answer(
        "📊 Прогресс:\n"
        "Вода:\n"
        f"- Выпито: {int(user['logged_water'])} мл из {water_goal} мл.\n"
        f"- Осталось: {water_remaining} мл.\n\n"
        "Калории:\n"
        f"- Потреблено: {int(user['logged_calories'])} ккал из {user['calorie_goal']} ккал.\n"
        f"- Сожжено: {int(user['burned_calories'])} ккал.\n"
        f"- Баланс: {int(net_calories)} ккал.\n"
        f"- Осталось: {int(calorie_remaining)} ккал.",
        reply_markup=MAIN_KEYBOARD,
    )
