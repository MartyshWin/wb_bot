import asyncio
import os
import logging
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiorun import run  # Импортируем aiorun

from app.commons.utils.custom_logger import setup_logger
from app.middlewares.logging import LoggingMiddleware
from app.routes.callbacks import main_router_callbacks
from app.routes.handlers import main_router
from config.config import settings


async def main() -> None:
    """
    Основная функция для запуска бота.
    """
    try:
        # Будет еще писаться информация о боте, имя, url, описание
        logging.info("🟢 Программа работает.")

        # Инициализация бота и диспетчера
        bot = Bot(
            token=settings.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode=settings.bot.parse_mode)
        )
        dp = Dispatcher()

        # Подключение Middleware
        dp.update.middleware(LoggingMiddleware())

        # Подключение обработчиков
        dp.include_routers(
            main_router,
            main_router_callbacks
        )
        # Запуск бота
        await asyncio.sleep(0.7)
        logging.info("🔄 Запуск long polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"📛 Ошибка в главной функции: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        setup_logger(settings.logging.level)
        # logger = logging.getLogger(__name__)
        logging.info("🚀 Запуск бота через aiorun...")

        run(main())
    except KeyboardInterrupt:
        logging.warning("Программа была остановлена вручную.")
    except Exception as e:
        logging.error(f"Ошибка во время выполнения программы: {e}", exc_info=True)