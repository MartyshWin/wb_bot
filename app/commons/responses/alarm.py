import logging
from datetime import datetime, date, timedelta
from pprint import pprint
from typing import AnyStr, Any, Optional, Sequence, Union

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.commons.responses.extensions import BaseHandlerExtensions, T
from app.commons.services.task import TaskService
from app.commons.utils.language_loader import load_language
from app.enums.constants import BOX_TITLES, COEF_TITLES, PERIOD_MAP
from app.enums.general import TaskMode, BoxType
from app.keyboards.inline.general import InlineKeyboardHandler
from app.routes.states.task_states import TaskStates
from app.schemas.general import ResponseModel, ResponseBoxTypes, ResponseCoefs


class TaskAlarmResponse(BaseHandlerExtensions):
    def __init__(self, inline_handler: InlineKeyboardHandler):
        super().__init__()
        self.task_service = TaskService()
        self.inline = inline_handler
        self.task_state_template: dict[str, Any] = {
            'current_page': 0,
            'list': [],
            'selected_list': [],
            'box_type': [],
            'coefs': None,
            'period_start': None,
            'period_end': None,
            'mode': ''
        }


    async def setup_notifications(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str]
    ) -> ResponseModel:
        try:
            user_id: int = cq.from_user.id
            username: str = cq.from_user.username
            self.lang = load_language(code_lang)


            return self.format_response(
                text=self.lang['text_setup_notifications'],
                keyboard=self.inline.alarm_setting
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    async def view_all_warehouses(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> ResponseModel:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            self.lang = load_language(code_lang)
            user_id: int = cq.from_user.id
            page: int = self.get_or_default(self.safe_get(data, 2), int, 0)
            # мы предусматриваем, что стоит ограничение в 30 складов, поэтому пагинации не требуется
            # offset: int = page * self.limit_whs_per_page
            offset: int = 0 * self.limit_whs_per_page

            # ── 2. получение данных ─────────────────────────────
            task_list_with_names = await self.task_service.get_user_uniq_task_alarm(user_id, self.limit_whs_per_page, offset)

            # ── 3. Ответ пользователю  ─────────────────────────────
            return self.format_response(
                text=self.lang['text_toggle_notifications'],
                keyboard=self.inline.create_alarm_list(task_list_with_names)
            )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)

    async def toggle_alarm_for_wh(
            self,
            cq: CallbackQuery,
            code_lang: str,
            data: list[str],
            state: FSMContext
    ) -> Union[ResponseModel, Sequence[ResponseModel]]:
        try:
            # ── 1. извлечение и валидация данных ─────────────────────────────
            self.lang = load_language(code_lang)
            user_id: int = cq.from_user.id
            wh_id: int = self.get_or_default(self.safe_get(data, 2), int, 0)
            popup_text = None

            # ── 2. обрабатываем логику переключения ──────────────────────────
            if wh_id == 0 and self.safe_get(data, 1) == 'all':
                if self.safe_get(data, 2) == 'on':
                    toggle_on = await self.task_service.toggle_alarm_for_wh(user_id, 0, 1)
                    popup_text = self.format_alert(
                        popup_text=str(self.lang['alarm_on']),
                        popup_alert=True
                    )
                else:
                    toggle_off = await self.task_service.toggle_alarm_for_wh(user_id, 0, 0)
                    popup_text = self.format_alert(
                        popup_text=str(self.lang['alarm_off']),
                        popup_alert=True
                    )
            else:
                toggle_wh = await self.task_service.toggle_alarm_for_wh(user_id, wh_id)

            # ── 3. Ответ пользователю (ссылаясь на другую функцию) ──────────────────
            resp_upgrade = await self.view_all_warehouses(cq, code_lang, data, state)
            if popup_text:
                return [resp_upgrade, popup_text]

            return resp_upgrade
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in view_all_warehouses: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'], self.inline.my_tasks_empty)