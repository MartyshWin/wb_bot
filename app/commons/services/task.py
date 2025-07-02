import logging
from datetime import datetime, date
from pprint import pprint
from sqlalchemy.exc import SQLAlchemyError

# Импортируем типизацию
from typing import Any, Coroutine, Sequence, Union, Literal, Optional

# Импортируем родительский класс, расширяя его
from .extensions import BaseHandlerExtensions

# Импортируем класс для вывода системной информации и дампа данных
from ..utils.dump import DebugTools

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
    @BaseHandlerExtensions.with_session_and_error_handling
    async def handle_create_task(
            user_id: int,
            page: int = None,
            lang_dict: dict[str, dict[str, str]] | None = None,
            session=None
    ) -> dict:
        offset = page * 10 if page else 0
        # self.page_size
        # self.box_types

        # list_tasks = self.get_tasks_max_coef(user_id, box_types, {'limit': limit, 'offset': offset})
        # if list_tasks['text']:
        #     text = self.lang_dict['existing_tasks_warning'].format(list_tasks=list_tasks['text'])
        #     return {**self.format_response(text, 'tasks_update_all'), "total": list_tasks['total']}

        # return self.format_response(self.lang_dict['existing_tasks_warning'], 'tasks_append')
        return {'text': 'success'}

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def get_warehouses_page(
            limit: int = 30,
            offset: int = 0,
            mode: str = None,
            session=None
    ) -> ResponseWarehouses | ResponseError:
        rows = await hubs.get_all_warehouses(session, offset, limit)
        total_whs = await hubs.count_warehouses(session)

        warehouses = [{"id": w.warehouse_id, "name": w.warehouse_name} for w in rows]

        return ResponseWarehouses(
            warehouses=warehouses,
            mode=mode,
            offset=offset,
            limit=limit,
            total=total_whs
        )


    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def get_user_uniq_task_with_names(
            user_id: int,
            limit: Optional[int] = None,
            offset: Optional[int] = 0,
            session=None
    ) -> ResponseTasks | ResponseError:
        # ── 1. Получаем все уникальные задачи пользователя (по складам)
        uniq_task: Sequence[TaskRead] = await slots.get_tasks_unique_by_warehouse(session, user_id)

        # ── 1.1. Вытягиваем id складов и статус уведомлений в uniq_task_alarm;
        uniq_task_alarm = [{"id": task.warehouse_id, "alarm": task.alarm} for task in uniq_task if task.warehouse_id is not None]

        # ── 2. Получаем количество уникальных задач
        total = await slots.count_uniq_tasks_by_whs(session, user_id)

        # ── 3. Образуем список складов (whs_list) и получаем их имена (whs_names)
        whs_list = [w["id"] for w in uniq_task_alarm]
        whs_names = await hubs.get_warehouses_name_map(session, whs_list)

        # ── 4. Передаем в модель ResponseTasks
        return ResponseTasks(tasks=list(uniq_task), offset=offset, limit=limit, total=total,
                                  warehouses_names_list=whs_names)

        # DebugTools.pretty_dump(uniq_task, style="rich", title="📦 Product Dump")
        # DebugTools.pretty_dump(uniq_task_alarm, style="rich", title="📦 Product Dump")

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def get_user_uniq_task_warehouse_ids(
            user_id: int,
            session=None
    ) -> ResponseTasks | ResponseError:
        warehouses_ids = await slots.get_tasks_unique_by_warehouse(session, user_id)
        return ResponseTasks(tasks=list(warehouses_ids), offset=0, limit=1, total=0)

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def create_bulk_tasks(
            user_id: int,
            warehouse_ids: list[int],
            box_types: list[str],
            max_coef: int,
            days_range: list[datetime],
            session=None
    ):
        """Создаёт задачи на каждый день, склад, тип упаковки и коэффициент."""
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
    @BaseHandlerExtensions.with_session_and_error_handling
    async def get_all_unique_tasks(
            user_id: int,
            limit: int,
            offset: int = 0,
            session=None
    ) -> ResponseTasks | ResponseError:
        tasks = await slots.get_tasks_by_user_with_limit(session, user_id, limit, offset)
        tasks_serialized = [
            TaskRead.model_validate(task)
            for task in tasks
        ]
        total_whs_in_tasks = await slots.count_uniq_tasks_by_whs(session, user_id)

        return ResponseTasks(tasks=tasks_serialized, offset=offset, limit=limit, total=total_whs_in_tasks)

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def get_whs_by_ids(
            warehouses_ids: Sequence[int],
            session=None
    ) -> ResponseWarehouses | ResponseError:
        whs_by_ids = await hubs.get_warehouses_by_ids(session, warehouses_ids)
        warehouses: list[WarehouseRead] = [
            WarehouseRead.model_validate(wh) for wh in whs_by_ids
        ]
        return ResponseWarehouses(warehouses=warehouses, offset=0, limit=1, total=0)

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def get_wh_with_names(
            user_id: int,
            warehouses_ids: Sequence[int],
            session=None
    ) -> ResponseTasks | ResponseError:
        # ── 1. Получаем все уникальные задачи пользователя (по складам)
        uniq_task: Sequence[TaskRead] = await slots.get_tasks_by_user_and_wh(session, user_id, list(warehouses_ids))
        # single_task = ()

        # ── 1.1. Вытягиваем id складов и статус уведомлений в uniq_task_alarm;
        uniq_task_alarm = [{"id": task.warehouse_id, "alarm": task.alarm} for task in uniq_task if
                           task.warehouse_id is not None]

        # ── 2. Образуем список складов (whs_list) и получаем их имена (whs_names)
        whs_list = [w["id"] for w in uniq_task_alarm]
        whs_names = await hubs.get_warehouses_name_map(session, whs_list)

        # ── 3. Передаем в модель ResponseTasks
        return ResponseTasks(tasks=list(uniq_task), offset=0, limit=1, total=0,
                             warehouses_names_list=whs_names)

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def toggle_alarm_for_wh(
            user_id: int,
            warehouse_id: int,
            state: Optional[Literal[0, 1]] = None,
            session=None
    ) -> Literal[True] | ResponseError:
        """
        Обновляет состояние уведомлений:
        • если `state` не задан — переключает уведомление по конкретному складу;
        • если `state` задан — массово включает/отключает уведомления по всем складам.

        :param user_id: ID пользователя
        :param warehouse_id: ID склада (для одиночного изменения)
        :param state: Новое состояние (True / False), если массово
        :param session: Для декоратора (он автоматически заполняет этот параметр)
        :return: True при успехе, иначе — ResponseError
        """
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

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def delete_all_tasks(
            user_id: int,
            session=None
    ) -> Literal[True] | ResponseError:
        """
        Удаляет все задачи пользователя для указанного склада из таблицы `tasks`.

        :param user_id: ID пользователя
        :param session: Для декоратора (он автоматически заполняет этот параметр)
        :return: True при успехе, иначе — ResponseError
        """
        trash = await slots.delete_tasks_by_user(session, user_id)
        if trash > 0:
            return True

        return ResponseError(
            message=f"Ошибка при массовом удалении задач: user_id={user_id}",
            code="FIND_ALL_ERROR"
        )

    @staticmethod
    @BaseHandlerExtensions.with_session_and_error_handling
    async def delete_single_tasks(
            user_id: int,
            wh_id: int,
            session=None
    ) -> bool | ResponseError:
        """
        Удаляет все задачи пользователя для указанного склада из таблицы `tasks`.

        :param user_id: ID пользователя
        :param wh_id: ID склада (для одиночного удаления)
        :param session: Для декоратора (он автоматически заполняет этот параметр)
        :return: True при успехе, иначе — ResponseError
        """
        trash = await slots.delete_tasks_by_user_and_warehouse(session, user_id, wh_id)
        if trash > 0:
            return True

        return ResponseError(
            message=f"Ошибка при массовом удалении задач: user_id={user_id}",
            code="FIND_ALL_ERROR"
        )