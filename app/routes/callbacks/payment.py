from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from app.commons.responses.connection import ConnectionService
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = ConnectionService()
inline = InlineKeyboardHandler()


@router.callback_query(F.data.startswith('package_'))
async def select_package(callback_query: CallbackQuery) -> None | dict:
    """
    Обработчик кнопок интернета "X рублей - X Гб".

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    try:
        _, package = callback_query.data.split("_")

        user_lang = callback_query.from_user.language_code or "unknown"
        response = controller.package_selection_response(user_lang, package)

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        return {'logs_error': str(e)}

@router.callback_query(F.data == 'verify_payment')
async def verify_payment(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Проверить платеж".

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    try:
        user_lang = callback_query.from_user.language_code or "unknown"
        response = controller.connect_response(user_lang)

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
        # await callback_query.answer("Продолжаем с быстрым подключением.", show_alert=True)
    except Exception as e:
        return {'logs_error': str(e)}