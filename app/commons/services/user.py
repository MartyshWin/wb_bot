import logging
from typing import Any, Coroutine

from sqlalchemy.exc import SQLAlchemyError

from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
from ...models.alchemy_helper import db_helper
from ...models.crud.clients import user_exists_by_id, create_user
from ...schemas.user import UserRead, UserCreate


# from ...schemas.general import ResponseModel

class UserService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()

    @staticmethod
    async def user_exists(user_id: int) -> bool:
        try:
            async for session in db_helper.session_getter():
                return await user_exists_by_id(session, user_id)
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при проверке пользователя {user_id}: {e}", exc_info=True)
            return False

    @staticmethod
    async def create_default_user(user_id: int, username: str) -> UserRead | None:
        try:
            user_data = UserCreate(
                user_id=user_id,
                username=username,
                activity="start",
                bot_status=False,
            )
            async for session in db_helper.session_getter():
                created_user = await create_user(session, user_data)
                return UserRead.model_validate(created_user)  # Преобразуем ORM → Pydantic
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при создании пользователя {user_id}: {e}", exc_info=True)
            return None

    async def get_or_create_user(self, user_id: int, username: str) -> UserRead | None:
        if await self.user_exists(user_id):
            return UserRead(user_id=user_id, username=username)

        return await self.create_default_user(user_id, username)
