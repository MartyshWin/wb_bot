import logging
from typing import Any, Coroutine

from sqlalchemy.exc import SQLAlchemyError

from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel, ResponseWarehouses, ResponseError
from ...models.alchemy_helper import db_helper
# from ...models.crud.clients import user_exists_by_id, create_user
from ...models.crud.hubs import get_all_warehouses, count_warehouses
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

    async def select_warehouses_and_pages(
            self,
            user_id: int,
            page: int = None,
            lang_dict: dict[str, dict[str, str]] | None = None
    ) -> ResponseWarehouses | ResponseError:
        try:
            pass
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in select_warehouses_and_pages: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции select_warehouses_and_pages", code="INTERNAL_ERROR", errors=[str(e)])

    @staticmethod
    async def get_warehouses_page(
            limit: int = 30,
            offset: int = 0,
            mode: str = None,
    ) -> ResponseWarehouses | ResponseError:
        try:
            async for session in db_helper.session_getter():
                rows = await get_all_warehouses(session, offset, limit)
                # total_pages = -(-await count_warehouses(session) // limit)
                total_whs = await count_warehouses(session)
                warehouses = [{"id": w.warehouse_id, "name": w.warehouse_name} for w in rows]

                return ResponseWarehouses(warehouses=warehouses, mode=mode, offset=offset, limit=limit, total=total_whs)
            return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR", errors=[str(e)])