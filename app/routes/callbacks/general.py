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
@router.callback_query(F.data == 'main')
async def main(callback_query: CallbackQuery, state: FSMContext): #  -> None | dict - убрал, нет вызова return, который что-то бы возвращал
    """
    Обработчик кнопки "Главное меню".

    Логика работы:
    1. Вызывает метод `start_command_response`, который подготавливает текст и клавиатуру для главного меню.
    2. Обновляет текст текущего сообщения и кнопки, предоставляя пользователю доступ к основным функциям.

    Параметры:
    - callback_query (CallbackQuery): Объект, содержащий данные о взаимодействии пользователя с кнопкой.

    Возвращаемые данные:
    - Обновляет текст сообщения и кнопки для отображения главного меню.

    Используемые методы:
    - `start_command_response(user_id, username, code_lang)`:
      Подготавливает текст и клавиатуру для главного меню.

    Словарь текстов:
    - `response.text`: Текст главного меню.
    - `response.kb`: Клавиатура для главного меню.

    Примечания:
    - Эта функция используется для возвращения пользователя в главное меню после выполнения действий.
    - Логика обработки пользователя, его состояния или начальных данных централизована в методе `start_command_response`.

    Пример использования:
    - Пользователь нажимает кнопку "Главное меню", и ему отображается текст и кнопки главного меню.

    :param callback_query: CallbackQuery
    :param state: FSMContext
    :return: None | dict
    """
    await state.clear()
    try:
        user_lang = callback_query.from_user.language_code or "unknown"
        response = await controller.start_command_response(callback_query.from_user.id, callback_query.from_user.username, user_lang)

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e), exc_info=True)
#----------------------------------------#----------------------------------------