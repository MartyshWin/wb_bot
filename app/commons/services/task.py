import logging
from datetime import datetime, date
from pprint import pprint
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
from ...schemas.task import TaskCreate, TaskRead
from ...schemas.user import UserRead, UserCreate
from ...schemas.warehouse import WarehouseRead
from app.schemas.general import ResponseModel, ResponseWarehouses, ResponseError, ResponseTasks

# Импортируем crud модели целиком
from ...models.crud import slots, hubs


#----------------------------------------#----------------------------------------#
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
            async with db_helper.session_getter() as session:
                rows = await hubs.get_all_warehouses(session, offset, limit)
                # total_pages = -(-await hubs.count_warehouses(session) // limit)
                total_whs = await hubs.count_warehouses(session)
                warehouses = [{"id": w.warehouse_id, "name": w.warehouse_name} for w in rows]

                return ResponseWarehouses(warehouses=warehouses, mode=mode, offset=offset, limit=limit, total=total_whs)
            # return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR", errors=[str(e)])

    @staticmethod
    async def get_unique_warehouses_at_user(
            user_id: int,
            limit: int,
            offset: int = 0,
    ) -> ResponseWarehouses | ResponseError:
        try:
            async with db_helper.session_getter() as session:
                wid_at_user: list[dict[str, int | bool]] = await slots.get_warehouses_with_alarm(session, user_id)
                warehouse_ids = [w["id"] for w in wid_at_user]
                total_whs = await slots.count_unique_warehouses(session, user_id)
                warehouses = await hubs.get_warehouses_name_map(session, warehouse_ids)

                return ResponseWarehouses(warehouses=warehouses, offset=offset, limit=limit, total=total_whs, task_list=wid_at_user)
            # return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR",
                                 errors=[str(e)])

    @staticmethod
    async def create_bulk_tasks(
            user_id: int,
            warehouse_ids: list[int],
            box_types: list[str],
            max_coef: int,
            days_range: list[datetime],
    ):
        """Создаёт задачи на каждый день, склад, тип упаковки и коэффициент."""
        async with db_helper.session_getter() as session:
            for warehouse_id in warehouse_ids:
                for box_type_id in box_types:
                    for coef in range(max_coef + 1):
                        for task_date in days_range:
                            task_data = TaskCreate(
                                user_id=user_id,
                                warehouse_id=warehouse_id,
                                box_type_id=BOX_TYPE_MAP[box_type_id],
                                coefficient=coef,
                                state="new",
                                alarm=1,
                                date=task_date
                            )
                            transaction = await slots.create_task(session,  task_data)



    @staticmethod
    async def get_all_unique_tasks(
            user_id: int,
            limit: int,
            offset: int = 0,
    ) -> ResponseTasks | ResponseError:
        try:
            async with db_helper.session_getter() as session:
                tasks = await slots.get_tasks_by_user_with_limit(session, user_id, limit, offset)
                tasks_serialized = [
                    TaskRead.model_validate(task)
                    for task in tasks
                ]
                total_whs_in_tasks = await slots.count_unique_warehouses(session, user_id)

                return ResponseTasks(tasks=tasks_serialized, offset=offset, limit=limit, total=total_whs_in_tasks)
            # return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR",
                                 errors=[str(e)])

    @staticmethod
    async def get_whs_by_ids(
            warehouse_ids: Sequence[int]
    ) -> ResponseWarehouses | ResponseError:
        try:
            async with db_helper.session_getter() as session:
                whs_by_ids = await hubs.get_warehouses_by_ids(session, warehouse_ids)
                warehouses: list[WarehouseRead] = [
                    WarehouseRead.model_validate(wh) for wh in whs_by_ids
                ]
                return ResponseWarehouses(warehouses=warehouses, offset=0, limit=1, total=0)
            # return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in get_whs_by_ids: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR",
                                 errors=[str(e)])

    @staticmethod
    async def toggle_alarm_for_wh(
            user_id: int,
            warehouse_id: int,
            state: Optional[Literal[0, 1]] = None
    ) -> Literal[True] | ResponseError:
        """
        Обновляет состояние уведомлений:
        • если `state` не задан — переключает уведомление по конкретному складу;
        • если `state` задан — массово включает/отключает уведомления по всем складам.

        :param user_id: ID пользователя
        :param warehouse_id: ID склада (для одиночного изменения)
        :param state: Новое состояние (True / False), если массово
        :return: True при успехе, иначе — ResponseError
        """
        try:
            async with db_helper.session_getter() as session:
                if state is None:
                    # ── одиночное переключение ─────────────────────────────
                    toggle = await slots.toggle_alarm_state(session, user_id, warehouse_id)
                    if toggle > 0:
                        return True

                    return ResponseError(
                        message=f"Ошибка при поиске записи: warehouse_id={warehouse_id}, user_id={user_id}",
                        code="FIND_ERROR"
                    )

                # ── массовое изменение ─────────────────────────────────────
                toggle = await slots.set_alarm_state_all(session, user_id, state)
                if toggle > 0:
                    return True

                return ResponseError(
                    message=f"Ошибка при массовом изменении уведомлений: user_id={user_id}",
                    code="FIND_ALL_ERROR"
                )
            # return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in toggle_alarm_for_wh: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR",
                                 errors=[str(e)])

    @staticmethod
    async def delete_all_tasks(
            user_id: int,
    ) -> Literal[True] | ResponseError:
        """
        Удаляет все задачи пользователя для указанного склада из таблицы `tasks`.

        :param user_id: ID пользователя
        :return: True при успехе, иначе — ResponseError
        """
        try:
            async with db_helper.session_getter() as session:
                trash = await slots.delete_tasks_by_user(session, user_id)
                if trash > 0:
                    return True

                return ResponseError(
                    message=f"Ошибка при массовом удалении задач: user_id={user_id}",
                    code="FIND_ALL_ERROR"
                )
            # return ResponseError(message="Ошибка при подключении к базе данных", code="DATABASE_ERROR")
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in toggle_alarm_for_wh: {e}", exc_info=True)
            return ResponseError(message="Произошла ошибка в функции handle_create_task", code="INTERNAL_ERROR",
                                 errors=[str(e)])