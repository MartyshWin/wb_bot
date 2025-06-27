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
# Обработчик кнопки "Настройка уведомлений".
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('my_tasks'))
async def my_tasks(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    await state.clear()
    data, user_lang = await parse_cq(callback_query)
    response = await controller.overview_task(
        callback_query,
        user_lang,
        data,
        state
    )

    await template_callback(callback_query, state, inline,
        responses=response
    )