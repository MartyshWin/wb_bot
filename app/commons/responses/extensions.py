import json
import random
import string
import logging

from app.schemas.general import ResponseModel


class BaseHandlerExtensions:
    def __init__(self):
        self.lang: dict = {}

    @staticmethod
    def format_response(
        text: str | dict[str, object],
        keyboard: object | None = None,
        array_activity: bool = False,
        status: bool = True
    ) -> ResponseModel:
        """
        Форматирует ответ с текстом и клавиатурой в виде словаря.

        :param text: Текст ответа
        :param keyboard: Клавиатура для ответа (опционально)
        :param array_activity: Если передается словарь активностей
        :param status: Для указания статуса сообщения
        :return: Словарь с ключами 'status', 'text' и 'kb'
        """
        return ResponseModel(
            status=status,
            text=text['response'] if array_activity else text,
            kb=text['keyboard'] if array_activity else (keyboard or None)
        )