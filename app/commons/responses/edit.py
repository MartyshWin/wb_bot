import logging
from datetime import datetime, date, timedelta
from pprint import pprint
from typing import AnyStr, Any, Optional, Sequence, Union, Literal

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.commons.responses.extensions import BaseHandlerExtensions, T
from app.commons.services.task import TaskService
from app.commons.services.validators import date_validators
from app.commons.utils.language_loader import load_language
from app.enums.constants import BOX_TITLES, COEF_TITLES, PERIOD_MAP, BOX_TITLES_RU, BOX_TYPE_MAP
from app.enums.general import TaskMode, BoxType
from app.keyboards.inline.general import InlineKeyboardHandler
from app.routes.states.task_states import TaskStates
from app.schemas.general import ResponseModel, ResponseBoxTypes, ResponseCoefs
from app.schemas.typed_dict import LangType


class TaskEditResponse(BaseHandlerExtensions):
    def __init__(self, inline_handler: InlineKeyboardHandler):
        super().__init__()
        self.task_service = TaskService()
        self.inline = inline_handler
        self.prefix: str = 'task_update'

    # ───────────────────────────── commit ──────────────────────────────────────
    async def commit(
            self,
            user_id: int,
            cq: CallbackQuery,
            data: list[str],
            state: FSMContext,
            lang: LangType
    ) -> ResponseModel:
        code_lang = cq.from_user.language_code or "ru"
        wh_id: int = (await state.get_data()).get('update_task').get('list', [])[0]

        # ── 1. Удаление задач по этому wh id
        await self.task_service.delete_single_tasks(user_id, wh_id)

        # ── 2. Создание новых задач с этим id
        from app.commons.responses.task import TaskResponse
        task = TaskResponse(inline_handler=self.inline)
        await task.create_tasks_from_range(cq, code_lang, data, state, False, 'update_task')

        # ── 3. Перемещаем пользователя на список задач
        return await self.view_all_warehouses(cq, data, state, lang)

    # ───────────────────────────── end ──────────────────────────────────────

    async def view_all_warehouses(
            self,
            cq: CallbackQuery,
            data: list[str],
            state: FSMContext,
            lang: LangType
    ) -> ResponseModel:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            user_id: int = cq.from_user.id
            page: int = self.get_or_default(self.safe_get(data, 2), int, 0)
            # мы предусматриваем, что стоит ограничение в 30 складов, поэтому пагинации не требуется
            # offset: int = page * self.limit_whs_per_page
            offset: int = 0 * self.limit_whs_per_page

            # ── 2. получение данных ─────────────────────────────
            task_list_with_names = await self.task_service.get_user_uniq_task_with_names(user_id, self.limit_whs_per_page, offset)
            # self.debug.pretty_dump(task_list_with_names, style="rich", title="📦 Product Dump")

            # ── 3. Ответ пользователю и вывод складов, если склады есть ─────────────────────────────
            if task_list_with_names:
                return self.format_response(
                    text=lang['text_edit_task'],
                    keyboard=self.inline.create_alarm_list(
                        page_data=task_list_with_names,
                        url=f'{self.prefix}_select',
                        prefix_icon=('', ''),
                        alarm_helper_btn=False,
                        back='my_tasks'
                    )
                )
            else:
                return self.format_response(
                    text=lang['no_task'],
                    keyboard=self.inline.my_tasks_empty
                )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    async def view_select_warehouses(
            self,
            cq: CallbackQuery,
            data: list[str],
            state: FSMContext,
            lang: LangType
    ) -> ResponseModel:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            user_id: int = cq.from_user.id
            wh_id: int = self.get_or_default(self.safe_get(data, 3), int, 0)
            page: int = self.get_or_default(self.safe_get(data, 4), int, 0)

            # ── 2. получение данных ─────────────────────────────
            task_with_name = await self.task_service.get_wh_with_names(user_id,[wh_id])
            # self.debug.pretty_dump(task_with_name, style="rich", title="📦 task_with_name")

            # ── 2.1 группировка данных ─────────────────────────────
            single_task = self.extract_grouped_task_tuples(task_with_name.tasks)[0]

            # ── 3. объявление переменных ─────────────────────────────
            wh_name = task_with_name.warehouses_names_list[0]['name']
            box_ids, coef, time_start, time_end, active = single_task[1:]
            box_types = sorted(BOX_TITLES_RU.get(box, "Неизвестный тип") for box in box_ids)
            is_active = "🟢 АКТИВНО" if active else "🔴 НЕАКТИВНО"

            # ── 4. Ответ пользователю  ─────────────────────────────
            return self.format_response(
                text=lang['edit_task'].format(
                    warehouse=wh_name,
                    box=', '.join(box_types),
                    coef=coef,
                    period_start=time_start,
                    period_end=time_end,
                    status=is_active
                ),
                keyboard=self.inline.edit_task_warehouse(
                    warehouse_id = wh_id,
                    page = page
                )
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    # async def update_bt_wh(
    async def update_params_wh(
            self,
            cq: CallbackQuery,
            data: list[str],
            state: FSMContext,
            lang: LangType,
            lang_link: Literal['box_types', 'coef', 'period'] = "box_types"
    ) -> ResponseModel:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            user_id: int = cq.from_user.id
            wh_id: int = self.get_or_default(self.safe_get(data, 3), int, 0)
            page: int = self.get_or_default(self.safe_get(data, 4), int, 0)
            url_back = f"{self.prefix}_select_{wh_id}_{page}"

            # ── 2. получение данных ─────────────────────────────
            task_with_name = await self.task_service.get_wh_with_names(user_id,[wh_id])

            # ── 2.1 группировка данных ─────────────────────────────
            grouped = self.extract_grouped_task_tuples(task_with_name.tasks)[0]

            # ── 3. state (update_task)  ────────────────────────────────────────────
            # Создание машины состояний: FSMContext и базового словаря
            await state.clear()
            await state.set_state(TaskStates.update_task)

            # ── 4. объявление переменных  ─────────────────────────────
            wh_name     = task_with_name.warehouses_names_list[0]['name']
            box_ids, coef, time_start, time_end, active = grouped[1:]
            bt_labels = sorted(BOX_TITLES_RU.get(box, "Неизвестный тип") for box in box_ids)
            period_start = time_start.strftime("%Y-%m-%d")
            period_end   = time_end.strftime("%Y-%m-%d")
            # resolved box types
            rbt = [k for k, v in BOX_TYPE_MAP.items() if v in box_ids]
            # rbt = [next(k for k, v in BOX_TYPE_MAP.items() if v == i) for i in grouped[1]]

            # ── 5. Подготовка клавиатуры  ─────────────────────────────
            kb = default = None
            if lang_link == 'box_types':
                default = rbt
                kb = self.inline.box_type(
                    ResponseBoxTypes(
                        selected=rbt,
                        box_default=default,
                        warehouse_id=wh_id,
                        back=True
                    ),
                    BOX_TITLES,
                    f'{self.prefix}_selbox',
                    url_back
                )
            elif lang_link == 'coef':
                default = coef
                kb = self.inline.coefs(
                    ResponseCoefs(
                        selected=coef,
                        coef_default=default,
                        warehouse_id=wh_id,
                        back=True
                    ),
                    f'{self.prefix}_selcoef',
                    url_back
                )
            elif lang_link == 'period':
                default = (time_start, time_end)
                kb = self.inline.create_select_date(
                    f'{self.prefix}_seldate',
                    url_back,
                    f'{self.prefix}_diapason'
                )

            # ── 6. Обновление словаря  ─────────────────────────────
            await state.update_data(
                update_task=self._merge_setup_task(
                    self.task_state_template,
                    current_page=page,
                    list=[wh_id],
                    selected_list=[{'id': wh_id, 'name': wh_name}],
                    box_type=rbt,
                    coefs=coef,
                    period_start=period_start,
                    period_end=period_end,
                    default=default
                )
            )

            # ── 7. Ответ пользователю  ─────────────────────────────
            return self.format_response(
                text=lang['edit'][lang_link].format(
                    wh=wh_name,
                    box=', '.join(bt_labels),
                    coef=coef,
                    start=time_start,
                    end=time_end
                ),
                keyboard=kb
            )
        except Exception as e:
            # Логирование для отладки
            logging.exception(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    async def picked_elem(
            self,
            user_id,
            cq: CallbackQuery,
            data: list[str],
            state: FSMContext,
            lang: LangType,
            lang_link: Literal['box_types', 'coef', 'period', 'diapason'] = "box_types"
    ) -> ResponseModel | None:
        try:
            # ── 1. извлечение и валидация данных ────────────────────────────────
            page: int = self.get_or_default(self.safe_get(data, 5), int, 0)
            is_confirm = "confirm" in self.safe_get(data, 3)
            picked: str = self.get_or_default(self.safe_get(data, 3), str, '')

            # ── 2. state (update_task)  ──────────────────────────────────────────
            update_task: dict = (await state.get_data()).get('update_task')  # setup_task не может отсутствовать

            if picked in PERIOD_MAP:
                today = datetime.now().date()
                start, end = PERIOD_MAP[picked](today)

                is_confirm = True

                # ── 4.1 Обновление словаря, с подставленным новым значением ────────
                update_task = self._merge_setup_task(
                    update_task,
                    period_start=start.strftime("%Y-%m-%d"),
                    period_end=end.strftime("%Y-%m-%d")
                )


            # ── 3. получение id склада ─────────────────────────────────
            wh_id: int = self.get_or_default(self.safe_get(data, 4), int, update_task['list'][0])
            url_back = f"{self.prefix}_select_{wh_id}_{page}"

            # ── 4. Подготовка клавиатуры  ─────────────────────────────
            kb = None
            if lang_link == 'box_types':
                if picked != 'confirm':
                    update_task['box_type'] = self.toggle_selection(update_task.get("box_type", []), picked)

                kb = self.inline.box_type(
                    ResponseBoxTypes(
                        selected=update_task['box_type'],
                        box_default=update_task['default'],
                        warehouse_id=update_task['list'][0],
                        back=True
                    ),
                    BOX_TITLES,
                    f'{self.prefix}_selbox',
                    url_back
                )
            elif lang_link == 'coef':
                if str(picked).isdigit():
                    update_task['coefs'] = picked

                kb = self.inline.coefs(
                    ResponseCoefs(
                        selected=update_task['coefs'],
                        coef_default=update_task['default'],
                        warehouse_id=wh_id,
                        back=True
                    ),
                    f'{self.prefix}_selcoef',
                    url_back
                )
            elif lang_link == 'period':
                kb = self.inline.create_select_date(
                    f'{self.prefix}_seldate',
                    url_back,
                    f'{self.prefix}_seldiap'
                )

            # ── 5. Обновление словаря  ────────────────────────────────────────────────
            await state.update_data(update_task=update_task)

            # ── 6. confirm-ветка  ────────────────────────────────────────────────
            if is_confirm:
                return await self.commit(user_id, cq, data, state, lang)

            # ── 7. Подготовка labels  ─────────────────────────────
            bt_labels = (BOX_TITLES_RU.get(BOX_TYPE_MAP[bt], "Неизвестный тип") for bt in update_task['box_type'])

            # ── 8. Ответ пользователю  ─────────────────────────────
            return self.format_response(
                text=lang['edit'][lang_link].format(
                    wh=update_task['selected_list'][0]['name'],
                    box=', '.join(bt_labels),
                    coef=update_task['coefs'],
                    start=update_task['period_start'],
                    end=update_task['period_end']
                ),
                keyboard=kb
            )
        except Exception as e:
            # Логирование для отладки
            logging.exception(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    async def diapason(
            self,
            user_id,
            cq: CallbackQuery,
            data: list[str],
            state: FSMContext,
            lang: LangType,
            action: Optional[str]
    ) -> ResponseModel | None:
        try:
            # ── 1. state (update_task)  ──────────────────────────────────────────
            update_task: dict = (await state.get_data()).get('update_task')  # setup_task не может отсутствовать
            print(update_task)

            # ── 2. извлечение и валидация данных ────────────────────────────────
            wh_id: int = update_task['list'][0]
            page: int = update_task['current_page']
            url_back = f"{self.prefix}_select_{wh_id}_{page}"
            picked_action = self.safe_get(data, 3)
            is_confirm = "confirm" in picked_action if not picked_action is None else False
            picked: str = self.get_or_default(self.safe_get(data, 3), str, '')
            url_list = {
                'url': f'{self.prefix}_seldiap',
                'url_confirm': f'{self.prefix}_seldiap_confirm',
                'url_back': url_back,
                'url_change': f'{self.prefix}_seldiap'
            }

            # ── 2.1. подготовка переменных для учета даты
            pick_y: Optional[int | str]  = self.safe_get(data, 3)
            pick_m: Optional[int | str] = self.safe_get(data, 4)
            pick_d: Optional[int | str] = self.safe_get(data, 5)

            # ── 3. импорт модуля, для переиспользования функций
            from app.commons.responses.task import TaskResponse
            task_resp = TaskResponse(inline_handler=self.inline)

            if pick_y and pick_m and pick_d is None:
                return await task_resp.commit_month_selection(
                    pick_y, pick_m, url_list
                )
            elif action == 'seldiap' and not is_confirm:
                return await task_resp.commit_day_selection(
                    update_task, self.lang, state, pick_y, pick_m, pick_d, url_list, "update_task"
                )
            elif is_confirm:
                return await self.commit(user_id, cq, data, state, lang)

            # ── 4. Убираем период
            update_task = self._merge_setup_task(update_task, period_start='', period_end='')
            await state.update_data(update_task=update_task)

            # ── 4. Подготовка клавиатуры  ─────────────────────────────
            kb = self.inline.generate_calendar(
                **url_list
            )

            # ── 5. Обновление словаря  ────────────────────────────────────────────────
            # await state.update_data(update_task=update_task)

            # ── 6. confirm-ветка  ────────────────────────────────────────────────
            # if is_confirm:
            #     print(update_task)
            #     return await self.commit(user_id, cq, data, state, lang)

            # ── 7. Подготовка labels  ─────────────────────────────
            bt_labels = (BOX_TITLES_RU.get(BOX_TYPE_MAP[bt], "Неизвестный тип") for bt in update_task['box_type'])

            # ── 8. Ответ пользователю  ─────────────────────────────
            return self.format_response(
                text=lang['edit']['diapason'].format(
                    wh=update_task['selected_list'][0]['name'],
                    box=', '.join(bt_labels),
                    coef=update_task['coefs'],
                    start=update_task['default'][0].isoformat(),
                    end=update_task['default'][1].isoformat()
                ),
                keyboard=kb
            )
        except Exception as e:
            # Логирование для отладки
            logging.exception(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)


    async def handle_task_update(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel:
        try:
            # ── 1. извлечение и валидация данных
            self.lang = load_language(code_lang)
            user_id: int = cq.from_user.id
            action: Optional[str] = self.get_or_default(self.safe_get(data, 2), str, None)

            # ── 2. извлечение и валидация данных
            if action is None:
                return await self.view_all_warehouses(cq, data, state, self.lang)
            # ── 2.1. если выбран режим диапазона ──────────────────────────────
            elif action == "page":
                return await self.view_all_warehouses(cq, data, state, self.lang)
            elif action == "select":
                return await self.view_select_warehouses(cq, data, state, self.lang)

            # ── 2.2. Редактирование типов короба
            elif action == "box":
                return await self.update_params_wh(cq, data, state, self.lang, 'box_types')
            elif action == "selbox":
                return await self.picked_elem(user_id, cq, data, state, self.lang, 'box_types')

            # ── 2.3. Редактирование коэффициентов
            elif action == "coef":
                return await self.update_params_wh(cq, data, state, self.lang, 'coef')
            elif action == "selcoef":
                return await self.picked_elem(user_id, cq, data, state, self.lang, 'coef')

            # ── 2.4. Редактирование даты
            elif action == "date":
                return await self.update_params_wh(cq, data, state, self.lang, 'period')
            elif action == "seldate":
                return await self.picked_elem(user_id, cq, data, state, self.lang, 'period')

            # ── 2.5. Отрисовка и выбор диапазона
            elif action == "diapason":
                return await self.diapason(user_id, cq, data, state, self.lang, action)
            elif action == "seldiap":
                return await self.diapason(user_id, cq, data, state, self.lang, action)

            # self.debug.pretty_dump(task_list_with_names, style="rich", title="📦 Product Dump")

        except Exception as e:
            # Логирование для отладки
            logging.exception(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)