def workout_rate_per_min(workout_type: str) -> int:
    workout_type = workout_type.lower()
    rates = {
        "бег": 10,
        "run": 10,
        "ходьба": 4,
        "walk": 4,
        "велосипед": 8,
        "вело": 8,
        "bike": 8,
        "плавание": 9,
        "swim": 9,
        "силовые": 6,
        "силовая": 6,
        "weights": 6,
        "йога": 3,
        "yoga": 3,
    }
    for key, value in rates.items():
        if key in workout_type:
            return value
    return 5


def extra_water_for_minutes(minutes: int) -> int:
    return (minutes // 30) * 200
