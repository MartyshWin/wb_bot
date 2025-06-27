from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.task import TaskResponse
from app.commons.utils.template_callback import parse_cq, template_callback
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
inline = InlineKeyboardHandler()
controller = TaskResponse(inline_handler=inline)

#----------------------------------------#----------------------------------------
# Логика обновления типа короба
#----------------------------------------#----------------------------------------
@router.callback_query(F.data == "task_delete_confirm")
async def delete_confirm_yes(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    """
    Обработчик подтверждения удаления всех задач.

    Логика работы:
    1. Редактирует текст сообщения, отображая предупреждение о подтверждении удаления всех задач.
    2. Устанавливает новую клавиатуру для подтверждения действия.
    3. Отправляет пользователю всплывающее уведомление (alert) с дополнительным предупреждением.

    Параметры:
    - callback_query (CallbackQuery): Объект, содержащий данные о взаимодействии пользователя с кнопкой.

    Возвращаемые данные:
    - Редактирует текст сообщения и отображает клавиатуру для подтверждения.
    - Показывает всплывающее сообщение пользователю.

    Примечания:
    - Используется клавиатура `inline.delete_confirm` для отображения кнопок подтверждения.
    - Текст предупреждения берётся из словаря `App.text_responses_ru`, ключи:
        - 'confirm_delete_tasks': текст сообщения с подтверждением.
        - 'update_warning': текст всплывающего уведомления.
    """
    data, user_lang = await parse_cq(callback_query)
    response = await controller.delete_task(
        callback_query,
        user_lang,
        data,
        state
    )

    await template_callback(callback_query, state, inline,
        responses=response
    )
#----------------------------------------#----------------------------------------
# Логика удаления задачи в списке "Редактирования задач"
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('task_delete_'))
async def edit_task_box(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    data, user_lang = await parse_cq(callback_query)
    response = await controller.delete_task(
        callback_query,
        user_lang,
        data,
        state
    )

    await template_callback(callback_query, state, inline,
        responses=response
    )