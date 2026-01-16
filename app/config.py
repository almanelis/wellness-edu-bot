import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    telegram_bot_token: str
    openweather_api_key: str | None


def load_config() -> Config:
    load_dotenv()

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env or environment.")

    openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
    return Config(
        telegram_bot_token=telegram_bot_token,
        openweather_api_key=openweather_api_key,
    )
