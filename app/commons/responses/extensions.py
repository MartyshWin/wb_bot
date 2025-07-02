import json
import random
import string
import logging
from collections import defaultdict
from datetime import date, datetime

# Импортируем типизацию
from typing import TypeVar, Hashable, Sequence, Iterable, Union, Any, Optional, Tuple, get_args

from ..services.task import TaskService
# Импортируем класс для вывода системной информации и дампа данных
from ..utils.dump import DebugTools

# Импортируем enums модели и константы
from ...enums.constants import BOX_TITLES_RU, BOX_TITLES
from app.enums.general import TaskMode

# Импортируем pydantic модели
from ...schemas.task import TaskRead
from app.schemas.general import ResponseModel
from ...schemas.typed_dict import LangType

# T = TypeVar("T", bound=Hashable) - использовать значения в ключах словарей (dict), складывать в множества (set)
T = TypeVar("T")

# то, что можно скормить функции: либо готовая модель, либо «нечто»,
# из чего `format_response()` сделает модель (str / dict / kwargs ...)
ResponseInput = Union[ResponseModel, str, dict[str, Any]]

class BaseHandlerExtensions:
    def __init__(self):
        self.lang: LangType = {}
        self.debug = DebugTools
        self.limit_whs_per_page: int = 30
        self.limit_whs_for_view: int = 10

        self.task_state_template: dict[str, Any] = {
            'current_page': 0,
            'list': [],
            'selected_list': [],
            'box_type': [],
            'coefs': None,
            'period_start': None,
            'period_end': None,
            'mode': '',
            'existing_tasks_ids': [],
            'default': []
        }

        self.BULLET_HUBS = "\n\t 📍"  # единый разделитель для складов
        self.BULLET_BOXES = "\n\t ▫️"  # единый разделитель для типов упаковок
        # text = self.lang.get("create_task_list", {}).get("space", "🔒 no text")


    @staticmethod
    def format_response(
        text: str | dict[str, object],
        keyboard: Optional[object] = None,
        array_activity: bool = False,
        status: bool = True,
        popup_text: Optional[str] = None,
        popup_alert: Optional[bool] = None,
        type_edit: Optional[str] = 'message'
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
        # Явные "пустые" значения
        if value in (None, "None", "null", ""):
            return default

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

    # ───────────────────────────── helpers ──────────────────────────────────────
    @staticmethod
    def _parse_raw(raw: str | int) -> tuple[int, Optional[int], bool, bool]:
        """raw → (page, warehouse_id | None, is_id, is_confirm)"""
        if isinstance(raw, str):
            if raw.startswith("id"):
                return 0, int(raw[2:]), True, False
            if raw.startswith("confirm"):
                return 0, None, False, True
            return int(raw), None, False, False
        return int(raw), None, False, False

    @staticmethod
    def _merge_setup_task(old: dict, **patch) -> dict:
        """Иммутабельное обновление setup_task"""
        return {**old, **patch}

    @staticmethod
    def toggle_selection(
            container: Union[list[T], dict[T, Any]],
            key: T | None,
            *,
            single: bool = False,  # single=True → режим «один выбранный» (FLEX)
            value: Any = None,  # payload для словаря при первом добавлении
    ) -> Union[list[T], dict[T, Any]]:
        """
        Универсальный «переключатель» выбора.

        • container – либо список ID / Enum-ов      (list[T])
                      либо словарь {ID|Enum: any}   (dict[T, Any])
        • key       – элемент, по которому кликнули (int, Enum …)
                      None → контейнер остаётся без изменений
        • single    – True  → после добавления остаётся только key
                      False → мультивыбор
        • value     – чем заполнять dict при добавлении (по умолчанию None)

        Возвращается НОВЫЙ объект (исходный не мутируется).
        """

        if key is None:  # клик был «мимо» – ничего не меняем
            return container.copy() if isinstance(container, list) else container.copy()

        # ─────────────── работа со СПИСКОМ ─────────────────────────────
        if isinstance(container, list):
            if key in container:  # снять выбор
                return [x for x in container if x != key]

            # добавить
            return [key] if single else container + [key]

        # ─────────────── работа со СЛОВАРЁМ ────────────────────────────
        new_dict: dict[T, Any] = container.copy()

        if key in new_dict:  # снять выбор
            new_dict.pop(key)
        else:  # добавить
            if single:
                new_dict = {key: value}  # оставить только key
            else:
                new_dict[key] = value

        return new_dict

    @staticmethod
    async def format_tasks_list(
            tasks: list[TaskRead],
            box_titles: BOX_TITLES_RU,
            task_service: TaskService,
    ) -> dict[str, object]:
        """
        Формирует текстовый список задач по складам с агрегацией параметров:
        группировка по складу, коэффициенту, объединение типов коробок и периода дат.

        :param tasks: Список задач модели TaskRead
        :param box_titles: Словарь с отображением ID типа упаковки в его название (например: {5: "Монопаллеты"}).
        :param task_service: Сервисный слой, предоставляющий методы для работы с задачами (например, получение складов по ID).
        :return: Словарь с текстом и количеством складов
        """
        split_line = "----------------------"
        today = datetime.now().date()
        result: list[str] = []

        # ── группировка задач ─────────────────────────────────────────────
        grouped = defaultdict(lambda: defaultdict(set))
        for task in tasks:
            grouped[task.warehouse_id][task.coefficient].add((task.box_type_id, task.date))

        wh_ids = list(grouped.keys())
        whs_by_ids = await task_service.get_whs_by_ids(wh_ids)
        wh_names = {wh.warehouse_id: wh.warehouse_name for wh in whs_by_ids.warehouses}

        for wh_id, coef_groups in grouped.items():
            name = wh_names.get(wh_id, f"Неизвестный склад (ID: {wh_id})")

            for coefficient, box_and_dates in coef_groups.items():
                box_types = sorted({box_titles.get(box, "Неизвестный тип") for box, _ in box_and_dates})
                dates = sorted({date for _, date in box_and_dates})

                if not dates:
                    continue

                date_from = dates[0].date() if isinstance(dates[0], datetime) else dates[0]
                date_to = dates[-1].date() if isinstance(dates[-1], datetime) else dates[-1]
                is_active = "🟢 АКТИВНО" if date_from <= today <= date_to else "🔴 НЕАКТИВНО"

                result.append(
                    f"🚛 СКЛАД: {name}\n"
                    f"🛠 СТАТУС: {is_active}\n"
                    f"📦 УПАКОВКА: {', '.join(box_types)}\n"
                    f"⚖️ КОЭФФИЦИЕНТ: до х{coefficient}\n"
                    f"📅 ПЕРИОД ПОИСКА СЛОТОВ: с <u>{date_from}</u> по <u>{date_to}</u>"
                )

        return {
            "text": f"\n{split_line}\n".join(result),
            "total": len(wh_ids)
        }

    def toggle_id(self, items: list[int], wid: Optional[int], mode: TaskMode) -> list[int]:
        """
        «Переключает» склад *wid* в списке *items*, используя общий toggle_selection.

        • wid is None       → список не меняется
        • wid уже в items   → удаляем его
        • wid нет в items   → добавляем
        • mode == FLEX      → после добавления остаётся только wid (одиночный выбор)

        Возвращается **новый** список id.
        """
        # if wid is None:  # клик не по складу
        #     return items.copy()
        #
        # return self.toggle_selection(
        #     container=items,
        #     key=wid,
        #     single=(mode is TaskMode.FLEX),
        # )
        single = mode is TaskMode.FLEX
        return self.toggle_selection(items, wid, single=single)

    def build_selection_pieces(self, state: dict[str, Any]) -> dict[str, str]:
        """
        Возвращает **словарь** готовых фрагментов текста.
        Ключи добавляются только если данные действительно есть.

        keys:
            warehouses  – «📍 Алматы …»
            boxes       – «▫️ Короба …»
            coef        – «Бесплатно» / «До xN»
        """
        pieces: dict[str, str] = {'warehouses': '', 'boxes': '', 'coef': ''}

        # ── 1. склады ───────────────────────────────────────────────────────
        warehouses: list[dict[str, str | int]] = state.get("selected_list") or []
        if warehouses:
            pieces["warehouses"] = self.BULLET_HUBS.join(
                f"<i>{wh['name']}</i>" for wh in warehouses
            )

        # ── 2. типы коробок ────────────────────────────────────────────────
        box_codes: list = state.get("box_type") or []
        if box_codes:
            pieces["boxes"] = self.BULLET_BOXES.join(
                f"<i>{BOX_TITLES[code]}</i>" for code in box_codes
            )

        # ── 3. коэффициент ─────────────────────────────────────────────────
        raw_coef = state.get("coefs")
        if str(raw_coef).isdigit():
            coef = int(raw_coef)
            pieces["coef"] = (
                "Бесплатно" if coef == 0 else f"До <b>x{coef}</b>"
            )

        return pieces

    @staticmethod
    def extract_grouped_task_tuples(tasks: Sequence[TaskRead]) -> list[tuple[int, list[int], int, date, date, bool]]:
        """
        Группирует задачи по складу (warehouse_id), определяя:
        - список типов упаковки
        - максимальный коэффициент
        - начальную и конечную дату периода
        - активность задачи на текущую дату

        :return: список кортежей (warehouse_id, box_type_ids, max_coef, start_date, end_date, is_active)
        """
        grouped: dict[int, set[tuple[int, int, datetime]]] = defaultdict(set)

        for task in tasks:
            grouped[task.warehouse_id].add((task.box_type_id, task.coefficient, task.date))

        today = datetime.now().date()
        result: list[tuple[int, list[int], int, date, date, bool]] = []

        for warehouse_id, entries in grouped.items():
            box_types = sorted({box_id for box_id, _, _ in entries})
            coefficients = [coef for _, coef, _ in entries]
            dates = sorted({dt.date() if isinstance(dt, datetime) else dt for _, _, dt in entries})

            if not dates:
                continue

            max_coef = max(coefficients)
            period_start = dates[0]
            period_end = dates[-1]
            is_active = period_start <= today <= period_end

            result.append((warehouse_id, box_types, max_coef, period_start, period_end, is_active))

        return result