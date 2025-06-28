import json
import random
import string
import logging
from functools import wraps
from typing import TypeVar, Callable, Coroutine, Any

from app.models.alchemy_helper import db_helper
from app.schemas.general import ResponseModel, ResponseError

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])

class BaseHandlerExtensions:
    def __init__(self):
        self.lang: dict = {}
        self.box_types: dict[int, str] = {5: 'Монопаллеты', 6: 'Суперсейф', 2: 'Короба'}
        self.page_size: int = 10

    @staticmethod
    def with_session_and_error_handling(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                async with db_helper.session_getter() as session:
                    return await func(*args, session=session, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return ResponseError(
                    message=f"Произошла ошибка в функции {func.__name__}",
                    code="INTERNAL_ERROR",
                    errors=[str(e)]
                )

        return wrapper  # type: ignore
