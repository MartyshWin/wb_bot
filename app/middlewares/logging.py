from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, TelegramObject
import logging

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования всех CallbackQuery.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Логируем событие
        logging.debug(f"Middleware вызван для события: {type(event).__name__}")

        # Проверяем, является ли событие `CallbackQuery`
        if isinstance(event, Update) and event.callback_query:
            logging.debug(f"Получен CallbackQuery: {event.callback_query.data}")

        # Продолжаем выполнение обработчика
        return await handler(event, data)