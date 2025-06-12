import logging

from app.commons.responses.extensions import BaseHandlerExtensions
from app.commons.services.task import TaskService
from app.commons.utils.language_loader import load_language
from app.schemas.general import ResponseModel


class TaskResponse(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()
        self.task_service = TaskService()

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
            mode: str
    ) -> ResponseModel:
        try:
            self.lang = load_language(code_lang)

            user = await self.task_service.get_warehouses_page(user_id, )
            print(user)
            # return self.format_response(
            #     text=self.lang['create_task_list']['space'],
            #     keyboard='task_mode_keyboard'
            # )
        except Exception as e:
            # Логирование для отладки
            logging.error(f"Error in handle_create_task: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'])