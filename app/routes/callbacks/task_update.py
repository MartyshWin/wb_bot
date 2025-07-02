from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.edit import TaskEditResponse
from app.commons.utils.template_callback import parse_cq, template_callback
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
inline = InlineKeyboardHandler()
controller = TaskEditResponse(inline_handler=inline)

#----------------------------------------#----------------------------------------
# Обработчик кнопки "✏️ Редактировать задачи".
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('task_update'))
async def task_update(callback_query: CallbackQuery, state: FSMContext): #  -> None | dict - убрал, нет вызова return, который что-то бы возвращал
    data, user_lang = await parse_cq(callback_query)
    response = await controller.handle_task_update(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(callback_query, state, inline,
        responses=response
    )