import logging
from sqlalchemy.exc import SQLAlchemyError

# Импортируем типизацию
from typing import Any, Coroutine, Sequence, Union, Literal, Optional

# Импортируем родительский класс, расширяя его
from .extensions import BaseHandlerExtensions

# Импортируем enums модели и константы
from ...enums.constants import BOX_TYPE_MAP

# Импортируем Хэлпер для алхимии, предоставляет доступ к базе
from ...models.alchemy_helper import db_helper

# Импортируем pydantic модели
from ...schemas.user import UserRead, UserCreate
from app.schemas.general import ResponseModel, ResponseWarehouses, ResponseError, ResponseTasks

# Импортируем crud модели целиком
from ...models.crud import clients


#----------------------------------------#----------------------------------------#
class UserService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()

    @staticmethod
    async def user_exists(user_id: int) -> bool:
        try:
            async with db_helper.session_getter() as session:
                return await clients.user_exists_by_id(session, user_id)
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при проверке пользователя {user_id}: {e}", exc_info=True)
            return False

    @staticmethod
    async def create_default_user(user_id: int, username: str) -> UserRead:
        try:
            user_data = UserCreate(
                user_id=user_id,
                username=username,
                activity="start",
                bot_status=False,
            )
            async with db_helper.session_getter() as session:
                created_user = await clients.create_user(session, user_data)
                return UserRead.model_validate(created_user)  # Преобразуем ORM → Pydantic
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при создании пользователя {user_id}: {e}", exc_info=True)

    async def get_or_create_user(self, user_id: int, username: str) -> UserRead:
        if await self.user_exists(user_id):
            return UserRead(user_id=user_id, username=username)

        return await self.create_default_user(user_id, username)
