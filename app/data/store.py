users: dict[int, dict] = {}


def get_user(user_id: int) -> dict:
    if user_id not in users:
        users[user_id] = {
            "weight": None,
            "height": None,
            "age": None,
            "gender": None,
            "activity": None,
            "city": None,
            "water_goal": 0,
            "calorie_goal": 0,
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0,
            "extra_water_from_workouts": 0,
            "pending_food": None,
        }
    return users[user_id]


def has_profile(user: dict) -> bool:
    return all(
        user.get(key) is not None
        for key in ("weight", "height", "age", "activity", "city")
    )
