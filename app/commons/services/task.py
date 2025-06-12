import logging
from typing import Any, Coroutine

from sqlalchemy.exc import SQLAlchemyError

from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
from ...models.alchemy_helper import db_helper
# from ...models.crud.clients import user_exists_by_id, create_user
from ...models.crud.slots import 
from ...schemas.user import UserRead, UserCreate

# Перенести в TaskResponse
class TaskService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()

    async def handle_create_task(
            self,
            user_id: int,
            page: int = None,
            lang_dict: dict[str, dict[str, str]] | None = None
    ) -> dict:
        try:
            offset = page * 10 if page else 0
            # self.page_size
            # self.box_types

            # list_tasks = self.get_tasks_max_coef(user_id, box_types, {'limit': limit, 'offset': offset})
            # if list_tasks['text']:
            #     text = self.lang_dict['existing_tasks_warning'].format(list_tasks=list_tasks['text'])
            #     return {**self.format_response(text, 'tasks_update_all'), "total": list_tasks['total']}

            # return self.format_response(self.lang_dict['existing_tasks_warning'], 'tasks_append')
            return {'text': 'success'}
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return {'error': 'error occurred'}


    async def get_warehouses_page(
            self,
            user_id: int,
            page: int = None,
            lang_dict: dict[str, dict[str, str]] | None = None
    ) -> dict:
        try:
            async for session in db_helper.session_getter():
                return await user_exists_by_id(session, user_id)

            return {'text': 'success'}
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return {'error': 'error occurred'}