import json
import random
import string
import logging
from typing import TypeVar, Hashable, Literal, Sequence

from app.schemas.general import ResponseModel

T = TypeVar("T", bound=Hashable)

class BaseHandlerExtensions:
    def __init__(self):
        self.lang: dict[str, dict[str, str]] = {}
        # text = self.lang.get("create_task_list", {}).get("space", "🔒 no text")

    @staticmethod
    def format_response(
        text: str | dict[str, object],
        keyboard: object | None = None,
        array_activity: bool = False,
        status: Literal[True] = True
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

    @staticmethod
    def safe_get(
            seq: Sequence[T],
            index: int,
            default: T | None = None,
    ) -> T | None:
        """
        Безопасно возвращает элемент `seq[index]`, не поднимая `IndexError`.

        data = ["zero", "one", "two"]
        element = safe_get(data, 1)                 # → "one"
        element = safe_get(data, 10)                # → None
        element = safe_get(data, 10, default="-")   # → "-"
        element = safe_get(data, -1)                # → "two"

        letters = ("a", "b", "c")
        element = safe_get(letters, 0)              # → "a"

        • seq     – любой индексируемый контейнер (`list`, `tuple`, `str`, …)
        • index   – целевой индекс (поддерживаются и отрицательные)
        • default – значение по умолчанию, если индекс вне диапазона
        """
        return seq[index] if -len(seq) <= index < len(seq) else default