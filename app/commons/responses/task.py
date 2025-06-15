import logging
from pprint import pprint
from typing import AnyStr, Any, Optional, Sequence, Union

from aiogram.fsm.context import FSMContext

from app.commons.responses.extensions import BaseHandlerExtensions, T
from app.commons.services.task import TaskService
from app.commons.utils.language_loader import load_language
from app.enums.constants import BOX_TITLES
from app.enums.general import TaskMode, BoxType
from app.keyboards.inline.general import InlineKeyboardHandler
from app.routes.states.task_states import TaskStates
from app.schemas.general import ResponseModel, ResponseBoxTypes, ResponseCoefs


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

        self.BULLET_HUBS = "\n\t 📍"  # единый разделитель для складов
        self.BULLET_BOXES = "\n\t ✔️"  # единый разделитель для типов упаковок


    async def handle_create_task(
            self,
            user_id: int,
            username: str,
            code_lang: str,
            data: list[str]
    ) -> ResponseModel:
        try:
            self.lang = load_language(code_lang)

            raw_page = self.safe_get(data, 2)  # str | None
            page: int | None = int(raw_page) if raw_page is not None else None

            # page = int(data[2]) if len(data) > 2 else None  # int(data[2]) if len(data) > 2 else 0

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
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    # ───────────────────────────── helpers ──────────────────────────────────────
    # Подумать стоит ли переносить эти хэлперы в отдельный модуль
    @staticmethod
    def _parse_raw(raw: str | int) -> tuple[int, Optional[int], bool, bool]:
        """raw → (page, warehouse_id | None, is_id, is_confirm)"""
        if isinstance(raw, str):
            if raw.startswith("id"):
                return 0, int(raw[2:]), True, False
            if raw.startswith("confirm"):
                return 0, None, False, True
            return int(raw), None, False, False
        return int(raw), None, False, False

    @staticmethod
    def _merge_choose_wh(old: dict, **patch) -> dict:
        """Иммутабельное обновление choose_wh"""
        return {**old, **patch}

    @staticmethod
    def toggle_selection(
            container: Union[list[T], dict[T, Any]],
            key: T | None,
            *,
            single: bool = False,  # single=True → режим «один выбранный» (FLEX)
            value: Any = None,  # payload для словаря при первом добавлении
    ) -> Union[list[T], dict[T, Any]]:
        """
        Универсальный «переключатель» выбора.

        • container – либо список ID / Enum-ов      (list[T])
                      либо словарь {ID|Enum: any}   (dict[T, Any])
        • key       – элемент, по которому кликнули (int, Enum …)
                      None → контейнер остаётся без изменений
        • single    – True  → после добавления остаётся только key
                      False → мультивыбор
        • value     – чем заполнять dict при добавлении (по умолчанию None)

        Возвращается НОВЫЙ объект (исходный не мутируется).
        """

        if key is None:  # клик был «мимо» – ничего не меняем
            return container.copy() if isinstance(container, list) else container.copy()

        # ─────────────── работа со СПИСКОМ ─────────────────────────────
        if isinstance(container, list):
            if key in container:  # снять выбор
                return [x for x in container if x != key]

            # добавить
            return [key] if single else container + [key]

        # ─────────────── работа со СЛОВАРЁМ ────────────────────────────
        new_dict: dict[T, Any] = container.copy()

        if key in new_dict:  # снять выбор
            new_dict.pop(key)
        else:  # добавить
            if single:
                new_dict = {key: value}  # оставить только key
            else:
                new_dict[key] = value

        return new_dict

    def toggle_id(self, items: list[int], wid: Optional[int], mode: TaskMode) -> list[int]:
        """
        «Переключает» склад *wid* в списке *items*, используя общий toggle_selection.

        • wid is None       → список не меняется
        • wid уже в items   → удаляем его
        • wid нет в items   → добавляем
        • mode == FLEX      → после добавления остаётся только wid (одиночный выбор)

        Возвращается **новый** список id.
        """
        # if wid is None:  # клик не по складу
        #     return items.copy()
        #
        # return self.toggle_selection(
        #     container=items,
        #     key=wid,
        #     single=(mode is TaskMode.FLEX),
        # )
        single = mode is TaskMode.FLEX
        return self.toggle_selection(items, wid, single=single)

    async def commit_hubs_selection(
            self,
            state_data: dict,
            lang: dict[str, dict[str, str]],
    ) -> ResponseModel:
        warehouses_list: list[dict[str, str | int]] = state_data.get('selected_list')

        selected_warehouses = self.BULLET_HUBS.join(
            f"<i>{wh['name']}</i>"
            for wh in warehouses_list
        )
        box_schema = ResponseBoxTypes(
            selected=state_data.get('box_type', []),
            mode=state_data.get('mode')
        )
        return self.format_response(
            text=lang['selected_warehouse']["text"].format(selected_text=selected_warehouses),
            keyboard=self.inline.box_type(box_schema, BOX_TITLES)
        )

    async def commit_box_selection(
            self,
            state_data: dict,
            lang: dict[str, dict[str, str]],
    ) -> ResponseModel:
        warehouses_list: list[dict[str, str | int]] = state_data.get('selected_list')
        box_types: dict[str, str]

        selected_warehouses = self.BULLET_HUBS.join(
            f"<i>{wh['name']}</i>"
            for wh in warehouses_list
        )
        box = self.BULLET_BOXES.join(
            f"<i>{BOX_TITLES[code]}</i>"
            for code in state_data.get('box_type')
        )

        coef_schema = ResponseCoefs(
            selected=state_data.get("coefs"),  # None или 0‥20
            mode=state_data.get("mode", TaskMode.FLEX),
        )
        return self.format_response(
            text=lang['selected_box_type']["text"].format(
                selected_text=selected_warehouses,
                box=box
            ),
            keyboard = self.inline.coefs(coef_schema)
        )

    # ───────────────────────────── handlers ──────────────────────────────────────
    async def handle_task_mode(
            self,
            user_id: int,
            username: str,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        """
        page           – номер страницы; 0, если клик был по складу ('id…'); page собирается из отсутствия is_id
        -> int: (0 if is_id else int(raw))

        selected_wid   – id выбранного склада, либо None; selected_wid собирается по срезу
        -> Optional[int]: (int(raw[2:]) if is_id else None)

        is_id          – флаг: клик по складу, проверка по id (raw начинается с 'id')
        -> bool: (raw.startswith("id") if isinstance(raw, str) else False)

        is_confirm     – флаг: клик по кнопке «Подтвердить», проверка по confirm (raw == 'confirm')
        -> bool: (raw.startswith("confirm") if isinstance(raw, str) else False)
        """
        try:
            self.lang = load_language(code_lang)

            # ── 1. mode (enum) ────────────────────────────────────────────────────
            raw_mode = self.safe_get(data, 2)
            mode: TaskMode = (
                TaskMode(raw_mode)  # превращаем в Enum
                if raw_mode in TaskMode._value2member_map_  # проверка «значение ∈ enum»
                else TaskMode.FLEX  # дефолт
            )

            # ── 2. raw-параметры из callback ─────────────────────────────────────
            raw = self.safe_get(data, 3) or 0
            page, selected_wid, is_id, is_confirm = self._parse_raw(raw)

            # ── 3. state (choose_wh)  ────────────────────────────────────────────
            # Создание машины состояний: FSMContext и базового словаря
            state_data = await state.get_data()
            choose_wh: dict = state_data.get('choose_wh', self.task_state_template)
            logging.warning(choose_wh) # REMOVE

            # ── 4. confirm-ветка  ────────────────────────────────────────────────
            if choose_wh.get('list') and choose_wh.get('selected_list') and is_confirm:
                return await self.commit_hubs_selection(choose_wh, self.lang)

            # ── 5. пересчёт list / current_page / mode ───────────────────────────
            if (
                    choose_wh.get('current_page') != int(page) # Если страница в памяти != текущая
                    or selected_wid
                    or choose_wh.get('mode') != mode # сменился режим
            ):
                # ── 5.1. Очистка состояния и установка нового
                await state.clear()
                await state.set_state(TaskStates.context_data_choose_wh)

                # ── 5.2. Список складов согласно режиму
                whs_list: list[int] = self.toggle_id(choose_wh.get('list', []), selected_wid, mode)

                # ── 5.3. Обновление страницы в памяти, если была нажата кнопка НЕ со складом
                current_page: int = page if selected_wid is None else choose_wh.get('current_page')

                # ── 5.4. Обновление словаря, с подставленными новыми значениями
                choose_wh = self._merge_choose_wh(
                    choose_wh,
                    mode=mode,
                    list=whs_list, # Если flex, то будет просто обновляться whs_list
                    current_page=current_page,
                )
                await state.update_data(choose_wh=choose_wh)

            # ── 6. получаем страницу складов  ───────────────
            offset: int = choose_wh.get('current_page') * self.limit
            warehouses_page = await self.task_service.get_warehouses_page(self.limit, offset, mode)

            # ── 6.1. объединяем объекты: сначала «старые», потом текущая страница
            combined_wh = (
                    choose_wh.get('selected_list', [])  # то, что уже было сохранено
                    + warehouses_page.warehouses  # склады на текущей странице
            )

            # ── 6.2. Уберём дубликаты по id, чтобы не было повторов
            # Дубликатов быть не должно, потому что на каждой страницы другие склады
            # Но если ошибка в базе, то это спасет нас от этого
            unique_wh = {w['id']: w for w in combined_wh}.values()

            # ── 6.3. Фильтруем выбранные склады
            filtered: list[dict[str, str | int]] = (
                self.task_service.sync_selected_warehouses(
                    list(unique_wh),                        # полный справочник без дублей
                    choose_wh.get('list', [])               # выбранные id
                )
            )

            # ── 6.4. Обновление словаря
            choose_wh = self._merge_choose_wh(choose_wh, selected_list=filtered)
            await state.update_data(choose_wh=choose_wh)
            logging.warning(choose_wh)  # REMOVE

            # ── 7. Ответ пользователю  ───────────────────────────────────────────
            return self.format_response(
                text=self.lang['create_task_list'][f'task_mode_{mode.value}'],
                keyboard=self.inline.create_warehouse_list(
                    warehouses_page,
                    choose_wh['list'],
                    choose_wh['selected_list']
                )
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)


    async def handle_box_type(
            self,
            user_id: int,
            username: str,
            msg_text: str,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        try:
            self.lang = load_language(code_lang)

            # ── 1. state (choose_wh)  ────────────────────────────────────────────
            # Создание машины состояний: FSMContext и базового словаря
            state_data = await state.get_data()
            choose_wh: dict = state_data['choose_wh'] # choose_wh не может отсутствовать
            choose_bt: dict = state_data.get('choose_bt', {})

            # ── 1.1. Получаем mode, он не может отсутствовать
            mode: TaskMode = choose_wh['mode']

            # ── 2. Получение action и is_confirm из callback ─────────────────────
            action = self.safe_get(data, 2)
            is_confirm: bool = action.startswith("confirm")

            # ── 3. confirm-ветка  ────────────────────────────────────────────────
            if choose_bt and is_confirm:
                return await self.commit_box_selection(choose_bt, self.lang)

            # ── 4. box_type (enum) ───────────────────────────────────────────────
            if action not in BoxType._value2member_map_:
                raise ValueError("box_type не может быть пустым")
            box_type: BoxType = BoxType(action)  # mono, safe, pan

            # ── 5. Обновление выбранных типов ─────────────────────────────────────
            selected_bt: list[int] = self.toggle_selection(
                container=choose_bt.get("box_type", []),  # list[int]
                key=box_type.value,  # BoxType → int / str
            )

            # ── 6. Переход в следующее состояние ─────────────────────────────────
            await state.set_state(TaskStates.context_data_choose_box_type)

            # ── 7. Обновление словаря, с подставленными новыми значениями ────────
            choose_bt = self._merge_choose_wh(
                choose_wh,
                box_type=selected_bt,
            )
            await state.update_data(choose_bt=choose_bt)
            logging.warning(f"choose_bt: {choose_bt}\n choose_wh: {choose_wh}") # REMOVE

            # ── 6. Ответ пользователю ─────────────────────────────────
            box_schema = ResponseBoxTypes(
                selected=choose_bt.get('box_type', []),
                mode=mode
            )
            return self.format_response(
                text=msg_text,
                keyboard=self.inline.box_type(box_schema, BOX_TITLES)
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_box_type: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)