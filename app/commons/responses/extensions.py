import json
import random
import string
import logging
from datetime import date
from typing import TypeVar, Hashable, Sequence, Iterable, Union, Any, Optional, Tuple, get_args

from app.schemas.general import ResponseModel

T = TypeVar("T", bound=Hashable)
# то, что можно скормить функции: либо готовая модель, либо «нечто»,
# из чего `format_response()` сделает модель (str / dict / kwargs ...)
ResponseInput = Union[ResponseModel, str, dict[str, Any]]

class BaseHandlerExtensions:
    def __init__(self):
        self.lang: dict[str, dict[str, str]] = {}
        self.limit_whs_per_page: int = 30
        self.limit_whs_for_view: int = 10
        # text = self.lang.get("create_task_list", {}).get("space", "🔒 no text")


    @staticmethod
    def format_response(
        text: str | dict[str, object],
        keyboard: Optional[object] = None,
        array_activity: bool = False,
        status: bool = True,
        popup_text: Optional[str] = None,
        popup_alert: Optional[bool] = None,
        type_edit: Optional[str] = None
    ) -> ResponseModel:
        """
        Форматирует ответ с текстом и клавиатурой в виде словаря.

        :param text: Текст ответа
        :param keyboard: Клавиатура для ответа (опционально)
        :param array_activity: Если передается словарь активностей
        :param status: Для указания статуса сообщения
        :param popup_text: Текст для всплывающего окна
        :param popup_alert: Статус всплывающего окна, True - с подтверждением
        :param type_edit: Тип редактирования (message или keyboard)
        :return: Словарь с ключами 'status', 'text' и 'kb'
        """
        return ResponseModel(
            status=status,
            text=text['response'] if array_activity else text,
            kb=text['keyboard'] if array_activity else (keyboard or None),
            popup_text=popup_text,
            popup_alert=popup_alert,
            type_edit=type_edit
        )

    @staticmethod
    def format_alert(
            status: bool = True,
            popup_text: Optional[str] = None,
            popup_alert: Optional[bool] = None,
    ) -> ResponseModel:
        """
        Форматирует ответ с текстом и клавиатурой в виде словаря.

        :param text: Текст ответа
        :param keyboard: Клавиатура для ответа (опционально)
        :param array_activity: Если передается словарь активностей
        :param status: Для указания статуса сообщения
        :param popup_text: Текст для всплывающего окна
        :param popup_alert: Статус всплывающего окна, True - с подтверждением
        :param type_edit: Тип редактирования (message или keyboard)
        :return: Словарь с ключами 'status', 'text' и 'kb'
        """
        return ResponseModel(
            status=status,
            text='',
            kb=None,
            popup_text=popup_text,
            popup_alert=popup_alert,
        )

    def format_responses(
        self,
        *items: ResponseInput | Iterable[ResponseInput]
    ) -> list[ResponseModel]:
        """
        «Пакетный» форматтер.

        • принимает любое количество аргументов:
          - готовые `ResponseModel`;
          - str / dict (передаётся дальше в `format_response`);
          - итерируемые коллекции вышеперечисленного;
        • возвращает `list[ResponseModel]`, фильтруя `None`.
        """
        out: list[ResponseModel] = []

        for item in items:
            # --- коллекция (list / tuple / set …) --------------------------
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes, ResponseModel)):
                out.extend(self.format_responses(*item))          # рекурсия
                continue

            # --- уже готовая модель ---------------------------------------
            if isinstance(item, ResponseModel):
                out.append(item)
                continue

            # --- «сырые» данные → создаём модель через format_response ----
            try:
                model = format_response(text=item)           # type: ignore[arg-type]
            except Exception as e:
                raise TypeError(f"Неподдерживаемый тип для format_responses: {type(item)!r}") from e

            out.append(model)

        # удаляем возможные None (если format_response вернёт None)
        return [m for m in out if m is not None]

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

    @staticmethod
    def validate_ymd(year: int, month: int, day: int) -> date:
        """
        Проверяет, что `year-month-day` образуют реальную календарную дату.

        • при успехе — возвращает `datetime.date`;
        • при ошибке — бросает `ValueError`, где уже будет указана причина
          (например, «day is out of range for month»).
        """
        try:
            return date(year, month, day)
        except ValueError as exc:  # 31 фев, 30 фев … ← сюда
            raise ValueError(
                f"Неверная дата: {year:04d}-{month:02d}-{day:02d}"
            ) from exc


    @staticmethod
    def get_or_default(value: Any, expected_type: Union[type, Tuple[type, ...]], default: T) -> T:
        """
        Пытается привести значение к одному из ожидаемых типов.
        Если удаётся — возвращает приведённое значение, иначе — default.

        :param value: Значение для проверки и возможного преобразования.
        :param expected_type: Тип или кортеж типов (например, int, (int, float)).
        :param default: Значение по умолчанию, если приведение не удалось.
        :return: Приведённое значение или default.
        """
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)

        for typ in expected_type:
            try:
                casted = typ(value)
                if isinstance(casted, typ):
                    return casted
            except (ValueError, TypeError):
                continue

        return default