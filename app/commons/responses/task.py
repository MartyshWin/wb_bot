import logging
from collections import defaultdict
from datetime import datetime, date, timedelta
from http.client import responses
from pprint import pprint
from typing import AnyStr, Any, Optional, Sequence, Union

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.commons.responses.edit import TaskEditResponse
from app.commons.responses.extensions import BaseHandlerExtensions, T
from app.commons.services.task import TaskService
from app.commons.services.validators import date_validators
from app.commons.utils.language_loader import load_language
from app.enums.constants import BOX_TITLES, COEF_TITLES, PERIOD_MAP, BOX_TITLES_RU
from app.enums.general import TaskMode, BoxType
from app.keyboards.inline.general import InlineKeyboardHandler
from app.routes.states.task_states import TaskStates
from app.schemas.general import ResponseModel, ResponseBoxTypes, ResponseCoefs
from app.schemas.task import TaskRead
from app.schemas.typed_dict import LangType


class TaskResponse(BaseHandlerExtensions):
    def __init__(self, inline_handler: InlineKeyboardHandler):
        super().__init__()
        self.task_service = TaskService()
        self.inline = inline_handler

    async def commit_hubs_selection(
            self,
            state_data: dict,
            lang: LangType,
    ) -> ResponseModel:
        box_types: list = state_data.get('box_type')
        parts = self.build_selection_pieces(state_data)

        box_schema = ResponseBoxTypes(
            selected=box_types,
            mode=state_data.get('mode')
        )
        return self.format_response(
            text=lang['selected_warehouse']["text"].format(selected_text=parts['warehouses']),
            keyboard=self.inline.box_type(box_schema, BOX_TITLES)
        )

    async def commit_box_selection(
            self,
            state_data: dict,
            lang: LangType,
    ) -> ResponseModel:
        coef: Optional[int] = state_data.get('coefs', None)
        parts = self.build_selection_pieces(state_data)

        coef_schema = ResponseCoefs(
            selected=coef,
            mode=state_data.get("mode"),
        )
        return self.format_response(
            text=lang['selected_box_type']["text"].format(
                selected_text=parts['warehouses'],
                box=parts['boxes']
            ),
            keyboard = self.inline.coefs(coef_schema)
        )

    async def commit_coefs_selection(
            self,
            state_data: dict,
            lang: LangType,
    ) -> ResponseModel:
        parts = self.build_selection_pieces(state_data)

        return self.format_response(
            text=lang['selected_coefs']["text"].format(
                selected_text=parts['warehouses'],
                box=parts['boxes'],
                coef=parts['coef']
            ),
            keyboard = self.inline.select_date
        )

    async def commit_date_selection(
            self,
            state_data: dict,
            lang: LangType,
    ) -> ResponseModel:
        # warehouses_list: list[dict[str, str | int]] = state_data.get('selected_list')
        # box_types: list = state_data.get('box_type')
        # raw = state_data['coefs']
        # coef = int(raw) if str(raw).isdigit() else -1
        parts = self.build_selection_pieces(state_data)
        period_start = state_data.get('period_start') or None
        period_end = state_data.get('period_end') or None


        return self.format_response(
            text=lang['selected_parameters']["text"].format(
                selected_text=parts['warehouses'],
                box=parts['boxes'],
                coef=parts['coef'],
                period_start=period_start,
                period_end=period_end
            ),
            keyboard = self.inline.save_params()
        )

    async def commit_month_selection(
            self,
            year: str | int,
            month: str | int,
            kb_url_list: Optional[dict] = None,
    ) -> ResponseModel:
        y, m, d = map(int, (year, month, 1))  # str → int
        check_date = self.validate_ymd(y, m, d)  # либо дата, либо исключение

        # ── 1.1. Создаем словарь с безопасной распаковкой
        calendar_kwargs = {
            "year": check_date.year,
            "month": check_date.month,
            **(kb_url_list or {})  # добавит только если словарь есть
        }

        return self.format_response(
            text='',
            keyboard=self.inline.generate_calendar(**calendar_kwargs),
            type_edit='keyboard'
        )

    async def commit_day_selection(
            self,
            state_data: dict,
            lang: LangType,
            state: FSMContext,
            year: str | int,
            month: str | int,
            day: str | int,
            kb_url_list: Optional[dict] = None,
            task_key: str = "setup_task"
    ) -> ResponseModel:
        # ── 1. извлечение и валидация данных
        error: dict[str, str] = lang['error']['diapason']

        period_start = state_data.get('period_start') or None
        period_end = state_data.get('period_end') or None

        y, m, d = map(int, (year, month, day))  # str → int
        check_date = self.validate_ymd(y, m, d)  # либо дата, либо исключение
        readable_date = check_date.isoformat()

        # ── 1.1. Создаем словарь с безопасной распаковкой
        calendar_kwargs = {
            "year": check_date.year,
            "month": check_date.month,
            "highlight_day": check_date.day,
            **(kb_url_list or {})  # добавит только если словарь есть
        }

        ok, error_text = date_validators.validate_diapason(check_date, period_start, period_end, error)
        # ── 1.2. вызов alert
        if not ok:
            return self.format_alert(popup_text=error_text, popup_alert=True)

        # ── 2. если выбрана конечная дата
        if period_start:
            data = self._merge_setup_task(state_data, period_end=readable_date)
            await state.update_data(**{task_key: data})

            # calendar_kwargs = {
            #     "year": check_date.year,
            #     "month": check_date.month,
            #     "highlight_day": check_date.day,
            #     "confirm": True,
            #     **(kb_url_list or {})  # добавит только если словарь есть
            # } #REMOVE

            calendar_kwargs['confirm'] = True
            return self.format_response(
                text=lang['diapason_confirm'].format(
                    start_date=period_start,
                    select_date=readable_date
                ),
                keyboard=self.inline.generate_calendar(**calendar_kwargs)
            )

        # ── 2.1. если выбрана начальная дата
        data = self._merge_setup_task(state_data, period_start=readable_date)
        await state.update_data(**{task_key: data})
        print(f'{data=}')

        # ── 3. Ответ пользователю
        return self.format_response(
            text=lang['diapason_end'].format(date=readable_date),
            keyboard=self.inline.generate_calendar(**calendar_kwargs)
        )

    # ───────────────────────────── handlers ──────────────────────────────────────
    async def handle_create_task(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str]
    ) -> ResponseModel:
        try:
            user_id: int = cq.from_user.id
            username: str = cq.from_user.username
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


    async def handle_task_mode(
            self,
            cq: CallbackQuery,
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
            user_id: int = cq.from_user.id
            username: str = cq.from_user.username
            self.lang = load_language(code_lang)

            # ── 1. mode (enum) ────────────────────────────────────────────────────
            raw_mode = self.safe_get(data, 2)
            mode: TaskMode = (
                TaskMode(raw_mode)  # превращаем в Enum
                if raw_mode in TaskMode._value2member_map_  # проверка «значение ∈ enum»
                else TaskMode.MASS  # дефолт
            )

            # ── 2. raw-параметры из callback ─────────────────────────────────────
            raw = self.safe_get(data, 3) or 0
            page, selected_wid, is_id, is_confirm = self._parse_raw(raw)

            # ── 3. state (setup_task)  ────────────────────────────────────────────
            # Создание машины состояний: FSMContext и базового словаря
            state_data = await state.get_data()
            setup_task: dict = state_data.get('setup_task', self.task_state_template)
            logging.warning(setup_task) # REMOVE

            # ── 4. confirm-ветка  ────────────────────────────────────────────────
            if setup_task.get('list') and setup_task.get('selected_list') and is_confirm:
                return await self.commit_hubs_selection(setup_task, self.lang)

            # ── 5. пересчёт list / current_page / mode ───────────────────────────
            if (
                    setup_task.get('current_page') != int(page) # Если страница в памяти != текущая
                    or selected_wid
                    or setup_task.get('mode') != mode # сменился режим
            ):
                # ── 5.1. Очистка состояния и установка нового
                await state.clear()
                await state.set_state(TaskStates.context_data_setup_task)

                # ── 5.2. Список складов согласно режиму
                whs_list: list[int] = self.toggle_id(setup_task.get('list', []), selected_wid, mode)

                # ── 5.3. Обновление страницы в памяти, если была нажата кнопка НЕ со складом
                current_page: int = page if selected_wid is None else setup_task.get('current_page')

                # ── 5.4. Обновление словаря, с подставленными новыми значениями
                setup_task = self._merge_setup_task(
                    setup_task,
                    mode=mode,
                    list=whs_list, # Если flex, то будет просто обновляться whs_list
                    current_page=current_page,
                )
                await state.update_data(setup_task=setup_task)

            # ── 6. получаем страницу складов  ───────────────
            offset: int = setup_task.get('current_page') * self.limit_whs_per_page
            warehouses_page = await self.task_service.get_warehouses_page(self.limit_whs_per_page, offset, mode)

            # ── 6.1. объединяем объекты: сначала «старые», потом текущая страница
            combined_wh = (
                    setup_task.get('selected_list', [])  # то, что уже было сохранено
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
                    setup_task.get('list', [])               # выбранные id
                )
            )

            # ── 6.4. Получаем уже выбранные склады
            response_tasks = await self.task_service.get_user_uniq_task_warehouse_ids(
                user_id
            )
            existing_whs_ids = [task.warehouse_id for task in response_tasks.tasks if task.warehouse_id is not None]

            # ── 6.5. Обновление словаря
            setup_task = self._merge_setup_task(setup_task, selected_list=filtered, existing_tasks_ids=existing_whs_ids)
            await state.update_data(setup_task=setup_task)
            logging.warning(setup_task)  # REMOVE

            # ── 7. Ответ пользователю  ───────────────────────────────────────────
            return self.format_response(
                text=self.lang['create_task_list'][f'task_mode_{mode.value}'],
                keyboard=self.inline.create_warehouse_list(
                    warehouses_page,
                    setup_task['list'],
                    setup_task['selected_list'],
                    setup_task['existing_tasks_ids']
                )
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_task_mode: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)


    async def handle_box_type(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        try:
            user_id: int = cq.from_user.id
            username: str = cq.from_user.username
            msg_text: str = cq.message.text
            self.lang = load_language(code_lang)

            # ── 1. state (setup_task)  ────────────────────────────────────────────
            state_data = await state.get_data()
            setup_task: dict = state_data['setup_task'] # setup_task не может отсутствовать
            setup_task_bxts: list = setup_task.get('box_type', [])

            # ── 1.1. Получаем mode, он не может отсутствовать
            mode: TaskMode = setup_task['mode']

            # ── 2. Получение action и is_confirm из callback ─────────────────────
            action: int | str = self.safe_get(data, 2)
            is_confirm: bool = action.startswith("confirm")

            # ── 3. confirm-ветка  ────────────────────────────────────────────────
            if setup_task_bxts and is_confirm:
                return await self.commit_box_selection(setup_task, self.lang)

            # ── 4. box_type (enum) ───────────────────────────────────────────────
            if action not in BoxType._value2member_map_:
                raise ValueError("box_type не может быть пустым")
            box_type: BoxType = BoxType(action)  # mono, safe, pan

            # ── 5. Обновление выбранных типов ─────────────────────────────────────
            selected_bt: list[int] = self.toggle_selection(
                container=setup_task.get("box_type", []),  # list[int]
                key=box_type.value,  # BoxType → int / str
            )

            # ── 6. Обновление словаря, с подставленными новыми значениями ────────
            setup_task = self._merge_setup_task(
                setup_task,
                box_type=selected_bt,
            )
            await state.update_data(setup_task=setup_task)
            logging.warning(f"setup_task: {setup_task}") # REMOVE

            # ── 7. Ответ пользователю ─────────────────────────────────
            box_schema = ResponseBoxTypes(
                selected=setup_task.get('box_type', []),
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

    async def handle_coefs(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        try:
            user_id: int = cq.from_user.id
            username: str = cq.from_user.username
            msg_text: str = cq.message.text
            self.lang = load_language(code_lang)

            # ── 1. state (setup_task)  ────────────────────────────────────────────
            state_data = await state.get_data()
            setup_task: dict = state_data['setup_task'] # setup_task не может отсутствовать

            # ── 1.1. Получаем mode, он не может отсутствовать
            mode: TaskMode = setup_task['mode']

            # ── 2. Получение action и is_confirm из callback ─────────────────────
            # action - это и коэффициент и его подтверждение (а также может быть любое действие)
            action: int | str = self.safe_get(data, 1)
            is_confirm: bool = action.startswith("confirm")

            # ── 3. confirm-ветка  ────────────────────────────────────────────────
            if str(setup_task.get('coefs')).isdigit() and is_confirm:
                return await self.commit_coefs_selection(setup_task, self.lang)

            # ── 4. coefs (constants) ───────────────────────────────────────────────
            if not str(action).isdigit():
                raise ValueError(f"{action!r} не является целым числом")
            action = int(action)

            if action not in COEF_TITLES:
                raise ValueError(f"Коэффициент {action!r} неизвестен")

            # ── 5. Обновление выбранных типов ─────────────────────────────────────
            if setup_task.get('coefs') == action:
                coef = None
            else:
                coef = action

            # ── 6. Обновление словаря, с подставленным новым значением ────────
            setup_task = self._merge_setup_task(
                setup_task,
                coefs=coef,
            )
            await state.update_data(setup_task=setup_task)
            logging.warning(f"setup_task: {setup_task}") # REMOVE

            # ── 7. Ответ пользователю ─────────────────────────────────
            coef_schema = ResponseCoefs(
                selected=coef,
                mode=mode,
            )
            return self.format_response(
                text=msg_text,
                keyboard=self.inline.coefs(coef_schema)
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_box_type: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    async def handle_date(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        try:
            user_id: int = cq.from_user.id
            username: str = cq.from_user.username
            msg_text: str = cq.message.text
            self.lang = load_language(code_lang)

            # ── 1. state (setup_task)  ────────────────────────────────────────────
            # Создание машины состояний: FSMContext и базового словаря
            state_data = await state.get_data()
            setup_task: dict = state_data['setup_task'] # setup_task не может отсутствовать
            logging.warning(f"setup_task (start): {setup_task}")  # REMOVE

            # ── 1.1. Получаем mode, он не может отсутствовать
            mode: TaskMode = setup_task['mode']

            # ── 2. Получение action и type из callback ─────────────────────
            # type_act - date or diapason; action - это переданная временной период
            process: str = self.safe_get(data, 0)
            type_act: str = self.safe_get(data, 1)
            action: int | str = self.safe_get(data, 2)
            sel_year: int | str = self.safe_get(data, 2)
            sel_month: int | str = self.safe_get(data, 3)
            sel_day: int | str = self.safe_get(data, 4)

            # ── 3. вычисляем период ─────────────────────────────────────────
            if action not in PERIOD_MAP and type_act == "date":
                return self.format_response(
                    text=msg_text,
                    popup_text="Неизвестная дата",
                    popup_alert=True
                )
            # ── 3.1 если выбран режим диапазона ──────────────────────────────
            elif type_act == "diapason":
                setup_task = self._merge_setup_task(
                    setup_task,
                    period_start='',
                    period_end=''
                )
                await state.update_data(setup_task=setup_task)
                logging.warning(f"setup_task: {setup_task}")  # REMOVE

                return self.format_response(
                    text=self.lang['diapason_start'],
                    keyboard=self.inline.generate_calendar(
                        year=sel_year,
                        month=sel_month,
                    )
                )
            # ── 3.2 смена месяца в диапазоне  ──────────────────────────────
            elif process == "change" and type_act == "month":
                return await self.commit_month_selection(sel_year, sel_month)
            # ── 3.3 выбор дня в диапазоне дат ──────────────────────────────
            elif process == "select" and type_act == "day":
                return await self.commit_day_selection(setup_task, self.lang, state, sel_year, sel_month, sel_day)

            # ── 4. если это не подтверждение диапазона ──────────────────────────────
            if type_act != 'confirm':
                today = datetime.now().date()
                start, end = PERIOD_MAP[action](today)

                # ── 4.1 Обновление словаря, с подставленным новым значением ────────
                setup_task = self._merge_setup_task(
                    setup_task,
                    period_start=start.strftime("%Y-%m-%d"),
                    period_end=end.strftime("%Y-%m-%d")
                )
                await state.update_data(setup_task=setup_task)
                logging.warning(f"setup_task: {setup_task}") # REMOVE

            # ── 5. Ответ пользователю ─────────────────────────────────
            return await self.commit_date_selection(setup_task, self.lang)
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_box_type: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)


    async def create_tasks_from_range(self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext,
            next_view: bool = True,
            state_key: str = 'setup_task'
    ) -> ResponseModel | None:
        """
        Создаёт задачи на основе данных:
        • список складов
        • типы коробок
        • максимальный коэффициент
        • диапазон дат (start → end)
        """

        # ── 1. state (setup_task)  ────────────────────────────────────────────
        # Создание машины состояний: FSMContext и базового словаря
        state_data = await state.get_data()
        setup_task: dict = state_data[state_key]  # setup_task не может отсутствовать

        # ── 2. извлечение и валидация данных ─────────────────────────────
        user_id: int = cq.from_user.id

        warehouse_ids: list[int] = setup_task.get('list', [])
        box_types: list[str] = setup_task.get('box_type', [])
        max_coef: int = int(setup_task.get('coefs'))

        # ── 3. валидация и парсинг периода ───────────────────────────────
        start_str = setup_task.get('period_start')
        end_str = setup_task.get('period_end')

        if not start_str or not end_str:
            raise ValueError("Период должен быть указан (period_start и period_end).")

        period_start = datetime.strptime(start_str, "%Y-%m-%d").date()
        period_end = datetime.strptime(end_str, "%Y-%m-%d").date()

        if period_start > period_end:
            raise ValueError("Дата начала не может быть позже даты окончания.")

        # ── 4. генерация списка дат ──────────────────────────────────────
        days_range: list[datetime] = []
        current = period_start
        while current <= period_end:
            days_range.append(current)
            current += timedelta(days=1)

        # ── 5. генерация задач по комбинациям ────────────────────────────
        await self.task_service.create_bulk_tasks(user_id, warehouse_ids, box_types, max_coef, days_range)
        from app.routes.callbacks.task_view import my_tasks
        if next_view:
            return await self.overview_task(cq, code_lang, data, state)

    # ───────────────────────────── task_view ──────────────────────────────────────
    async def overview_task(self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel | None:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            user_id: int = cq.from_user.id
            msg_text: str = cq.message.text
            page: int = self.get_or_default(self.safe_get(data, 2), int, 0)
            offset: int = page * self.limit_whs_for_view
            self.lang = load_language(code_lang)

            # ── 2. Получение задач юзера ─────────────────────────────────
            all_tasks = await self.task_service.get_all_unique_tasks(user_id, self.limit_whs_for_view, offset)
            response_text = await self.format_tasks_list(all_tasks.tasks, BOX_TITLES_RU, self.task_service)

            # ── 3. Ответ пользователю, если задач нет ─────────────────────────────────
            if not all_tasks.tasks and all_tasks.total == 0:
                return self.format_response(
                    text=self.lang['no_task'],
                    keyboard=self.inline.my_tasks_empty
                )

            # ── 4. Ответ пользователю, если задачи есть ─────────────────────────────────
            return self.format_response(
                text=f"{self.lang['have_task']} {response_text['text']}\n\n{self.lang['task_status']}",
                keyboard=self.inline.generate_pagination_keyboard(
                    current_page=page, total_tasks=all_tasks.total, page_size=self.limit_whs_for_view, callback_data='my_tasks_',
                    base_keyboard=self.inline.my_tasks
                )
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in overview_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    # ───────────────────────────── task_delete ──────────────────────────────────────
    async def delete_task(self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> Union[ResponseModel, list[ResponseModel]] | None:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            user_id: int = cq.from_user.id
            action = self.safe_get(data, 2)
            self.lang = load_language(code_lang)

            # ── 2. Получение задач юзера ─────────────────────────────────
            if action == 'confirm':
                return self.format_response(
                    text=self.lang['confirm_delete_tasks'],
                    keyboard=self.inline.delete_confirm,
                    popup_text=str(self.lang['confirm_delete_tasks']),
                    popup_alert=True
                )
            elif action == 'all':
                await self.task_service.delete_all_tasks(user_id)
                return self.format_response(
                    text=self.lang['tasks_deleted'],
                    keyboard=self.inline.tasks_delete_all,
                )
            elif action.startswith("id"):
                trash = await self.task_service.delete_single_tasks(user_id, action[2:])
                popup_text = self.format_alert(
                    popup_text=str(self.lang['single_task_deleted']),
                    popup_alert=True
                )
                from app.commons.responses.edit import TaskEditResponse
                edit_response = TaskEditResponse(inline_handler=self.inline)
                return [
                    popup_text,
                    await edit_response.view_all_warehouses(cq, data, state, self.lang)
                ]


        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in delete_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)