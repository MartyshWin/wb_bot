import logging
from typing import Any, Coroutine, Sequence

from sqlalchemy.exc import SQLAlchemyError

from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel, ResponseWarehouses, ResponseError
from ...models.alchemy_helper import db_helper
# from ...models.crud.clients import user_exists_by_id, create_user
from ...models.crud.hubs import get_all_warehouses, count_warehouses, get_warehouses_by_ids
from ...schemas.user import UserRead, UserCreate

class TaskService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()

    @staticmethod
    def sync_selected_warehouses(
            all_warehouses: list[dict[str, str | int]],
            selected_ids: list[int],
    ) -> list[dict[str, str | int]]:
        """
        Возвращает список складов только с теми `id`, которые есть в `selected_ids`.

        • `all_warehouses` – полный справочник: [{'id': 218987, 'name': 'Алматы'}, …]
        • `selected_ids`   – актуальный набор выбранных ID: [218987, 324108]

        Результат всегда «синхронизирован»:
        – склады, id которых пропали из `selected_ids`, удаляются;
        – новые id добавляются (при условии, что они есть в справочнике).
        """
        # словарь справочника id → объект склада
        ref = {w["id"]: w for w in all_warehouses}

        # формируем «чистый» список только по актуальным id
        return [ref[w_id] for w_id in selected_ids if w_id in ref]

    @staticmethod
    async def handle_create_task(
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