from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from app.commons.services.connection import ConnectionService
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = ConnectionService()
inline = InlineKeyboardHandler()


@router.callback_query(F.data == 'manual_setup')
async def full_connect(callback_query: CallbackQuery) -> None | dict:
    """
    Обработчик кнопки "Настроить под себя".

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    try:
        user_lang = callback_query.from_user.language_code or "unknown"
        response = controller.information_alert_response(user_lang, 'full')

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        return {'logs_error': str(e)}

@router.callback_query(F.data == 'continue_setup:full')
async def continue_setup_full(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Продолжить" для полного подключения.

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    _, method = callback_query.data.split(":")

    await callback_query.answer("Продолжаем с полным подключением.", show_alert=True)