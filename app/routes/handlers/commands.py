from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
import logging

from app.commons.services.general import GeneralService
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = GeneralService()
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
        response = controller.start_command_response(user_lang, message.from_user.full_name)

        await message.answer(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e))

@router.message(Command('invite'))
async def invite_command_handler(message: Message, command: CommandObject) -> None | dict:
    """
    Обработка команды /invite с параметром и без.

    :param message: Сообщение от пользователя.
    :param command: Объект команды, содержащий дополнительные параметры.
    """
    try:
        user_lang = message.from_user.language_code or "unknown"
        response = controller.invite_command_response(user_lang)

        await message.answer(response.text)
    except Exception as e:
        logging.error("message:" + str(e))

@router.message(Command('help'))
async def help_command_handler(message: Message, command: CommandObject) -> None | dict:
    """
    Обработка команды /help с параметром и без.

    :param message: Сообщение от пользователя.
    :param command: Объект команды, содержащий дополнительные параметры.
    """
    try:
        user_lang = message.from_user.language_code or "unknown"
        response = controller.help_command_response(user_lang)

        await message.answer(response.text)
    except Exception as e:
        logging.error("message:" + str(e))

@router.message(Command('lang'))
async def lang_command_handler(message: Message, command: CommandObject) -> None | dict:
    """
    Обработка команды /lang с параметром и без.

    :param message: Сообщение от пользователя.
    :param command: Объект команды, содержащий дополнительные параметры.
    """
    try:
        user_lang = message.from_user.language_code or "unknown"
        response = controller.lang_command_response(user_lang)

        await message.answer(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e))

@router.message(Command('privacy'))
async def privacy_command_handler(message: Message, command: CommandObject) -> None | dict:
    """
    Обработка команды /privacy с параметром и без.

    :param message: Сообщение от пользователя.
    :param command: Объект команды, содержащий дополнительные параметры.
    """
    try:
        user_lang = message.from_user.language_code or "unknown"
        response = controller.privacy_command_response(user_lang)

        await message.answer(response.text)
    except Exception as e:
        logging.error("message:" + str(e))