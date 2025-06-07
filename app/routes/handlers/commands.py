from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
import logging

from app.commons.responses.general import GeneralResponse
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = GeneralResponse()
inline = InlineKeyboardHandler()

@router.message(Command('start'))
async def start_command_handler(message: Message, command: CommandObject) -> None | dict:
    """
    Обработка команды /start с параметром и без.

    :param message: Сообщение от пользователя.
    :param command: Объект команды, содержащий дополнительные параметры.
    """
    try:
        # await message.answer(response['text'], reply_markup=inline.get_keyboard(response['kb']))
        user_lang = message.from_user.language_code or "unknown"
        response = await controller.start_command_response(message.from_user.id, message.from_user.username, user_lang)

        await message.answer(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e))