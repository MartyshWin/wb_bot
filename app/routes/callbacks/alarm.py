from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.alarm import TaskAlarmResponse
from app.commons.utils.template_callback import parse_cq, template_callback
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
inline = InlineKeyboardHandler()
controller = TaskAlarmResponse(inline_handler=inline)


#----------------------------------------#----------------------------------------
# Обработчик кнопки "Настройка уведомлений".
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('alarm_setting'))
async def alarm_setting(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    data, user_lang = await parse_cq(callback_query)
    response = await controller.setup_notifications(callback_query, user_lang, data)

    await template_callback(callback_query, state, inline,
        responses=response
    )

#----------------------------------------#----------------------------------------
# Обработчик кнопки "Уведомление по складам" и вкл/откл уведомления о складе.
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('alarm_edit'))
async def alarm_edit(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)
    response = await controller.view_all_warehouses(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(callback_query, state, inline,
        responses=response
    )

@router.callback_query(F.data.startswith('toggle_alarm_'))
async def toggle_alarm(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)
    response = await controller.toggle_alarm_for_wh(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(callback_query, state, inline,
        responses=response
    )

@router.callback_query(F.data.startswith('alarm_all_'))
async def alarm_all(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)
    response = await controller.toggle_alarm_for_wh(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(callback_query, state, inline,
        responses=response
    )