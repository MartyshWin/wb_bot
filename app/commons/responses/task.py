import logging
from typing import AnyStr, Any, Optional

from aiogram.fsm.context import FSMContext

from app.commons.responses.extensions import BaseHandlerExtensions
from app.commons.services.task import TaskService
from app.commons.utils.language_loader import load_language
from app.enums.general import TaskMode
from app.keyboards.inline.general import InlineKeyboardHandler
from app.routes.states.task_states import TaskStates
from app.schemas.general import ResponseModel


class TaskResponse(BaseHandlerExtensions):
    def __init__(self, inline_handler: InlineKeyboardHandler):
        super().__init__()
        self.task_service = TaskService()
        self.inline = inline_handler
        self.limit: int = 30
        self.task_state_template: dict[str, Any] = {
            'current_page': 0,
            'list': [],
            'selected_list': [],
            'box_type': [],
            'coefs': '',
            'period_start': '',
            'period_end': '',
            'mode': ''
        }

    async def handle_create_task(
            self,
            user_id: int,
            username: str,
            code_lang: str,
            data: list[str]
    ) -> ResponseModel:
        try:
            self.lang = load_language(code_lang)
            page = int(data[2]) if len(data) > 2 else None  # int(data[2]) if len(data) > 2 else 0

            # check page, he can't be integer
            # offset = page * 10 if page else 0
            # self.page_size
            # self.box_types

            # list_tasks = self.get_tasks_max_coef(user_id, box_types, {'limit': limit, 'offset': offset})
            # if list_tasks['text']:
            #     text = self.lang_dict['existing_tasks_warning'].format(list_tasks=list_tasks['text'])
            #     return {**self.format_response(text, 'tasks_update_all'), "total": list_tasks['total']}

            # self.lang['existing_tasks_warning'] - Если уже есть задачи
            return self.format_response(
                text=self.lang['create_task_list']['space'],
                keyboard='task_mode_keyboard'
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'])

    async def handle_task_mode(
            self,
            user_id: int,
            username: str,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        try:
            self.lang = load_language(code_lang)
            # Mode: flex or mass with ENUMS
            mode: TaskMode = (
                TaskMode(data[2])   # пробуем создать enum
                if len(data) > 2 and data[2] in TaskMode.__members__.values()
                else TaskMode.FLEX  # дефолт
            )
            # raw проверка 3 элемента в data, is_id проверка на нажатие на склад по id
            raw = data[3] if len(data) > 3 else 0
            is_id: bool = raw.startswith("id") if isinstance(raw, str) else False
            # page собирается из отсутствия is_id, а склады selected_warehouse_id по срезу
            page: int = 0 if is_id else int(raw)
            selected_warehouse_id: Optional[int] = int(raw[2:]) if is_id else None

            # Создание машины состояний: FSMContext
            state_data = await state.get_data()
            # Создание базового словаря
            choose_wh: dict = state_data.get('choose_wh', self.task_state_template)
            logging.warning(choose_wh) # REMOVE

            # Если страница в памяти != текущая ИЛИ выбранный склад не найден в списке ИЛИ сменился режим
            if choose_wh.get('current_page') != int(page) or not selected_warehouse_id in choose_wh.get('list', []) or choose_wh.get('mode') != mode:
                # Очистка состояния и установка нового
                await state.clear()
                await state.set_state(TaskStates.context_data_choose_wh)
                # Зависимость выбора склада от режима
                if mode == TaskMode.FLEX:
                    whs_list: list = [selected_warehouse_id] if selected_warehouse_id is not None else choose_wh.get("list", [])
                else:
                    whs_list: list = [*choose_wh['list'], selected_warehouse_id] if selected_warehouse_id is not None else choose_wh.get("list", [])

                # Обновление страницы в памяти, если была нажата кнопка НЕ со складом
                current_page: int = page if selected_warehouse_id is None else choose_wh.get("current_page")
                # Обновление словаря, с подставленными новыми значениями
                choose_wh = {
                    **choose_wh,
                    'mode': mode,
                    'list': whs_list, # Если flex, то будет просто обновляться whs_list
                    'current_page': current_page
                }
                await state.update_data(choose_wh=choose_wh)

            # Создание смещения
            offset: int = choose_wh.get("current_page") * self.limit
            warehouses_page = await self.task_service.get_warehouses_page(self.limit, offset, mode)
            logging.warning(choose_wh)  # REMOVE

            return self.format_response(
                text=self.lang['create_task_list'][f'task_mode_{mode.value}'],
                keyboard=self.inline.create_warehouse_list(warehouses_page, choose_wh['list'], warehouses_page.warehouses)
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'])