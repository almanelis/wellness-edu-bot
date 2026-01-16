import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import load_config
from app.handlers import common, logs, profile


async def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        level=logging.INFO,
    )

    config = load_config()
    bot = Bot(token=config.telegram_bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher["config"] = config

    dispatcher.include_router(common.router)
    dispatcher.include_router(profile.router)
    dispatcher.include_router(logs.router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
