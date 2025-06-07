from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from app.commons.responses.general import GeneralResponse
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = GeneralResponse()
inline = InlineKeyboardHandler()


@router.callback_query(F.data == 'main')
async def main(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    """
    Обработчик кнопки "Главное меню" или "Назад".

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    await state.clear()
    try:
        user_lang = callback_query.from_user.language_code or "unknown"
        response = await controller.start_command_response(callback_query.from_user.id, callback_query.from_user.username, user_lang)

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e))