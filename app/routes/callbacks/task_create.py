from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.general import GeneralResponse
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = GeneralResponse()
inline = InlineKeyboardHandler()

#----------------------------------------#----------------------------------------
# Обработчик кнопки "Создать задачу".
# Перенести всю логику создания задачи в отдельный модуль
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('create_task'))
async def create_task_handler(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    data = callback_query.data.split("_")
    page = int(data[2]) if len(data) > 2 else 0
    # payment_status = SubCtrler.handler_payment(callback_query.from_user.id)
    # if payment_status['status']:
    #     await callback_query.message.answer(payment_status['text'])

    offset = page * 10 if page else 0
    page_size = 10

    response = App.handle_create_task(callback_query.from_user.id, box_types, page_size + offset, offset)
    if response.get("kb") == "tasks_append":
        await tasks_append(callback_query)
    else:
        kb = inline.generate_pagination_keyboard(
            current_page=page, total_tasks=response['total'], page_size=page_size, callback_data='create_task_',
            base_keyboard=inline.get_keyboard(response["kb"]) if response["kb"] else None
        )
        await callback_query.message.edit_text(
            text=response["text"],
            reply_markup=kb
        )