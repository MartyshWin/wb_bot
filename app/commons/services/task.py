import logging
from typing import Any, Coroutine

from sqlalchemy.exc import SQLAlchemyError

from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
from ...models.alchemy_helper import db_helper
from ...models.crud.clients import user_exists_by_id, create_user
from ...schemas.user import UserRead, UserCreate

class TaskService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()

    def handle_create_task(
            self,
            user_id: int,
            box_types: dict[int, str],
            limit: int = None,
            offset: int = None
    ) -> dict:
        """
        Обрабатывает логику кнопки "Создать задачу".

        - Проверяет подписку пользователя.
        - Если подписка активна, проверяет наличие задач.
        - Возвращает текст и клавиатуру для обработки в обработчике.

        :param user_id: int - ID пользователя.
        :param box_types: dict - ключ - значение для типа короба
        :param limit: int - ключ - для пагинации
        :param offset: int - ключ - для пагинации
        :return: dict - Форматированный ответ через format_response.
        """
        try:
            if not self.is_subscribed(user_id):
                return self.format_response(self.lang_dict['no_subscription'], 'subscribe')

            list_tasks = self.get_tasks_max_coef(user_id, box_types, {'limit': limit, 'offset': offset})
            if list_tasks['text']:
                text = self.lang_dict['existing_tasks_warning'].format(list_tasks=list_tasks['text'])
                return {**self.format_response(text, 'tasks_update_all'), "total": list_tasks['total']}

            return self.format_response(self.lang_dict['existing_tasks_warning'], 'tasks_append')
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}")
            return self.format_response(self.lang_dict['error_occurred'])