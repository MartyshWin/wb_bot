import logging
from typing import Union, Sequence, Iterable

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.schemas.general import ResponseModel

ResponseLike = Union["ResponseModel", Sequence["ResponseModel"]]

async def template_callback(
    cq: CallbackQuery,
    state: FSMContext,
    *,
    responses: ResponseLike,
):
    """
    Универсальный обработчик:
    • принимает 1 или несколько ResponseModel;
    • первый ответ редактирует исходное сообщение,
      остальные — отправляет новыми.
    """
    try:
        # 1. делаем список из любого входа
        resp_list: Sequence[ResponseModel] = (
            list(responses)
            if isinstance(responses, Iterable) and not isinstance(responses, dict)
            else [responses]
        )

        if not resp_list:
            return  # ничего показывать

        # 2. первый ответ → edit_text
        first = resp_list[0]
        if first.popup_text:
            await cq.answer(first.popup_text, show_alert=first.popup_alert)

        await cq.message.edit_text(first.text, reply_markup=first.kb)

        # 3. остальные ответы → send_message
        for resp in resp_list[1:]:
            if resp.popup_text:
                await cq.answer(resp.popup_text, show_alert=resp.popup_alert)

            await cq.message.answer(resp.text, reply_markup=resp.kb)

    except Exception as e:
        logging.error(f"template_callback error: {e}", exc_info=True)

async def parse_cq(cq: CallbackQuery):
    """
    Возвращает:
    • data       – список токенов callback-данных (split("_"))
    • user_lang  – язык пользователя или 'unknown'
    """
    data = cq.data.split("_")
    user_lang = cq.from_user.language_code or "unknown"
    return data, user_lang