from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.commons.services.connection import ConnectionService
from app.keyboards.inline.general import InlineKeyboardHandler
from app.routes.states.user_states import UserStates

router = Router()
controller = ConnectionService()
inline = InlineKeyboardHandler()


@router.callback_query(F.data == 'fast_connect')
async def fast_connect(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    """
    Обработчик кнопки "Быстрое подключение".

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    :param state: Объект, содержащий состояние бота.
    :return: None или словарь с ошибкой
    """
    try:
        user_lang = callback_query.from_user.language_code or "unknown"
        response = controller.information_alert_response(user_lang, 'fast')

        # Получаем текущие данные состояния
        # state_data = (await state.get_data()).get('configuring_connection')
        # state_data.append('')
        arr_data = {
            'choosing_connection_method': response.text,
            'method': 'fast',
            'list': {
                'data': response.kb
            }
        }

        await state.set_state(UserStates.configuring_connection)
        await state.update_data(context_data=arr_data)


        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        return {'logs_error': str(e)}


@router.callback_query(F.data == 'continue_setup:fast')
async def continue_setup_fast(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Продолжить" для быстрого подключения.

    :param callback_query: Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    """
    try:
        _, method = callback_query.data.split(":")

        user_lang = callback_query.from_user.language_code or "unknown"
        response = controller.get_packages_list_response(user_lang)

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
        # await callback_query.answer("Продолжаем с быстрым подключением.", show_alert=True)
    except Exception as e:
        return {'logs_error': str(e)}
