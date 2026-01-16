from aiogram.fsm.state import State, StatesGroup


class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    city = State()
    calorie_custom = State()
    calorie_value = State()


class FoodStates(StatesGroup):
    query = State()
    grams = State()


class WaterStates(StatesGroup):
    amount = State()


class WorkoutStates(StatesGroup):
    workout_type = State()
    minutes = State()
