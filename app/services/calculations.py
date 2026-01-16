from typing import Optional


def calculate_water_goal(
    weight: float,
    activity_minutes: int,
    temp_c: Optional[float],
) -> int:
    base = weight * 30
    activity_bonus = (activity_minutes // 30) * 500
    heat_bonus = 0
    if temp_c is not None:
        if temp_c > 30:
            heat_bonus = 1000
        elif temp_c > 25:
            heat_bonus = 500
    return int(base + activity_bonus + heat_bonus)


def calculate_calorie_goal(
    weight: float,
    height: float,
    age: int,
    activity_minutes: int,
    gender: Optional[str],
) -> int:
    base = 10 * weight + 6.25 * height - 5 * age
    if gender == "m":
        base += 5
    elif gender == "f":
        base -= 161
    activity_bonus = activity_minutes * 5
    return int(base + activity_bonus)


def parse_number(text: str) -> Optional[float]:
    try:
        return float(text.replace(",", ".").strip())
    except ValueError:
        return None


def parse_int(text: str) -> Optional[int]:
    value = parse_number(text)
    if value is None:
        return None
    if value <= 0:
        return None
    return int(value)
