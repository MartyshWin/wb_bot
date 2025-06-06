from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from app.commons.responses.general import GeneralResponse
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = GeneralResponse()
inline = InlineKeyboardHandler()


@router.callback_query(F.data == 'home')
async def main(callback_query: CallbackQuery) -> None | dict:
    """
    Обработчик кнопки "Главное меню" или "Назад".

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    try:
        user_lang = callback_query.from_user.language_code or "unknown"
        response = controller.start_command_response(user_lang, callback_query.from_user.full_name)

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        return {'logs_error': str(e)}