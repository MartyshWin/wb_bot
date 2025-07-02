import ast
import json
import re
import shlex
from itertools import batched
from sys import prefix
from typing import Union, Callable, List, Any, TypedDict, Optional, Iterable, Tuple, Sequence

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.enums.constants import COEF_TITLES
from app.enums.general import BoxType
from app.schemas.general import ResponseWarehouses, ResponseBoxTypes, ResponseCoefs, ResponseTasks


# Кнопки должны получать язык приложения, чтобы соответствовать выбранному пользователем
class InlineKeyboardHandler:
    def __init__(self):

        self.start_kb: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "📝 Создать список задач", "callback_data": "create_task"}],
            [{"text": "🗂 Мой список задач", "callback_data": "my_tasks"}],
            [{"text": "⚙️ Настройка уведомлений", "callback_data": "alarm_setting"}],
            [{"text": "💎 Подписка", "callback_data": "choose_tariff"}],
            [{"text": "ℹ️ Инструкция", "callback_data": "rules"}],
        ])

        self.task_mode_keyboard: InlineKeyboardMarkup = self.build_inline_keyboard([
            [
                {"text": "🛠️ Массовая настройка задач", "callback_data": "task_mode_mass"},
                {"text": "🔧 Гибкая настройка задач", "callback_data": "task_mode_flex"}
            ],
            [{"text": "🏠 Главное меню", "callback_data": "main"}],
        ])
        self.tasks_update_all: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "♻️ Создать новый список", "callback_data": "task_delete_confirm"}],
            [{"text": "✏️ Добавить к списку", "callback_data": "tasks_append"}],
            [{"text": "Назад ↩️", "callback_data": "main"}],
        ])

        self.delete_confirm: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "Да", "callback_data": "task_delete_all"}], # tasks_update_all
            [{"text": "Отмена", "callback_data": "main"}],
        ])

        self.tasks_delete_all: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "♻️ Создать новый список", "callback_data": "create_task"}],
            [{"text": "🏠 Главное меню", "callback_data": "main"}],
        ])

        # self.search_slot_mass: InlineKeyboardMarkup = self.build_inline_keyboard([
        #     [{"text": "🚀 Отправить в работу", "callback_data": "task_save"}],
        #     [{"text": "🏠 Главное меню", "callback_data": "main"}],
        # ])
        #
        # self.search_slot_flex: InlineKeyboardMarkup = self.build_inline_keyboard([
        #     [{"text": "🚀 Отправить в работу", "callback_data": "task_save"}],
        #     [{"text": "🏠 Главное меню", "callback_data": "main"}],
        # ])

        self.subscribe: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "💳 Оформить подписку", "callback_data": "choose_tariff"}],
            [{"text": "🆓 Получить 7 дней доступа", "callback_data": "free_sub"}],
            [{"text": "🏠 Главное меню", "callback_data": "main"}],
        ])

        self.bot_add: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "🚫 Отмена", "callback_data": "alarm_setting"}],
        ])

        self.choose_tariff: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "💼 Тариф \"СТАРТ\" (590 руб.)", "callback_data": "tarif_1"}],
            [{"text": "🚀 Тариф \"ПРОФИ\" (790 руб.)", "callback_data": "tarif_2"}],
            [{"text": "👑 Тариф \"МАКСИ\" (1390 руб.)", "callback_data": "tarif_3"}],
            [{"text": "Назад ↩️", "callback_data": "choose_tariff"}],
        ])

        self.choose_tariff_with_free: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "💼 Тариф \"СТАРТ\" (590 руб.)", "callback_data": "tarif_1"}],
            [{"text": "🚀 Тариф \"ПРОФИ\" (790 руб.)", "callback_data": "tarif_2"}],
            [{"text": "👑 Тариф \"МАКСИ\" (1390 руб.)", "callback_data": "tarif_3"}],
            [{"text": "🆓 Получить 7 дней доступа", "callback_data": "free_sub"}],
            [{"text": "Назад ↩️", "callback_data": "choose_tariff"}],
        ])

        self.my_tasks: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "📝 Добавить задачи", "callback_data": "create_task"}],
            [{"text": "✏️ Редактировать задачи", "callback_data": "task_update"}],
            [{"text": "🗑️ Удалить все задачи", "callback_data": "task_delete_confirm"}],
            [{"text": "Назад ↩️", "callback_data": "main"}],
        ])

        self.alarm_setting: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "🚀 Подключить бота уведомлений", "callback_data": "bot_add"}],
            [{"text": "⭐ Уведомления по складам", "callback_data": "alarm_edit"}],
            [{"text": "Назад ↩️", "callback_data": "main"}],
        ])

        self.my_tasks_empty: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "📝 Создать список задач", "callback_data": "create_task"}],
            [{"text": "🏠 Главное меню", "callback_data": "main"}],
        ])

        self.select_date = self.create_select_date()

        # self.select_date: InlineKeyboardMarkup = self.create_select_date()


    # def get_keyboard(self, attribute_name: str | object) -> str | None | Any:
    #     """
    #     Получает метод по имени и вызывает его с аргументами, если они указаны.
    #
    #     :param attribute_name: Имя метода и аргументы в формате 'method_name(arg1, arg2)'.
    #     :return: Результат выполнения метода или строка с ошибкой, если метод не найден.
    #     """
    #     # Проверяем, есть ли скобки в строке
    #     if attribute_name is not None:
    #         if '(' in attribute_name and attribute_name.endswith(')'):
    #             # Извлекаем имя метода и аргументы
    #             match = re.match(r"(\w+)\((.*)\)", attribute_name)
    #             if not match:
    #                 return "Invalid format"
    #
    #             method_name, args_str = match.groups()
    #
    #             # Получаем метод по имени
    #             method = getattr(self, method_name, None)
    #             if not method or not callable(method):
    #                 return "Not Found keyboard"
    #
    #             # Разделяем аргументы по запятой и убираем лишние пробелы
    #             args: List[str] = [arg.strip() for arg in args_str.split(',')] if args_str else []
    #
    #             # Вызываем метод с аргументами
    #             return method(*args)
    #         else:
    #             # Если скобок нет, просто вызываем метод без аргументов
    #             return getattr(self, attribute_name, "Not Found keyboard")

    def get_keyboard(self, call: Optional[str] = None) -> Any:
        """
        Динамически вызывает метод экземпляра по строке вида
        ``"method_name(1, 'txt', True)"`` или просто ``"property_name"``.

        :param call: Строка с вызовом или именем атрибута.
        :raises ValueError: Если формат строки некорректен.
        :raises AttributeError: Если метод/атрибут не найден.
        :raises TypeError: Если попытка вызвать не-callable.
        """
        if call is None:
            raise ValueError("call may not be None")

        # Вызов с аргументами
        if '(' in call and call.rstrip().endswith(')'):
            name, args = self._parse_call(call)
            method = self._get_callable(name)
            return method(*args)

        # Просто атрибут/метод без скобок
        attr = getattr(self, call, None)
        if attr is None:
            raise AttributeError(f"{call!r} not found in {self.__class__.__name__}")
        return attr() if callable(attr) else attr

    # ---- вспомогательные private-методы ----
    _call_re = re.compile(r"\s*(\w+)\s*\((.*)\)\s*")

    def _parse_call(self, text: str) -> tuple[str, List[Any]]:
        """Возвращает (имя, [аргументы])."""
        m = self._call_re.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid call syntax: {text!r}")

        name, arg_str = m.groups()
        if not arg_str.strip():
            return name, []

        lexer = shlex.shlex(arg_str, posix=True)
        lexer.whitespace_split = True
        lexer.whitespace = ','
        args = [ast.literal_eval(tok) for tok in lexer]
        return name, args

    def _get_callable(self, name: str) -> Callable[..., Any]:
        """Проверяет, что атрибут существует и является вызываемым."""
        attr = getattr(self, name, None)
        if attr is None:
            raise AttributeError(f"{name!r} not found in {self.__class__.__name__}")
        if not callable(attr):
            raise TypeError(f"{name!r} is not callable")
        return attr
    # ---------------------------

    @staticmethod
    def build_inline_keyboard(
            rows: list[list[dict[str, str | bool | dict | None]]]
    ) -> InlineKeyboardMarkup:
        """
        Принимает список строк, каждая строка — список кнопок (словарей с ключами text и callback_data/url/...).
        Возвращает InlineKeyboardMarkup с нужной раскладкой.
        """
        inline_keyboard = []

        for row in rows:
            button_row = []

            for btn in row:
                text = btn.get("text")
                if not text:
                    raise ValueError("Каждая кнопка должна содержать ключ 'text'.")

                action_keys = (
                    "callback_data",
                    "url",
                    "switch_inline_query",
                    "switch_inline_query_current_chat",
                    "callback_game",
                    "pay",
                )

                button_kwargs = {
                    key: btn[key] for key in action_keys if key in btn and btn[key] is not None
                }

                if not button_kwargs:
                    raise ValueError(f"Кнопка '{text}' не содержит допустимых параметров действия.")

                button = InlineKeyboardButton(text=text, **button_kwargs)
                button_row.append(button)

            inline_keyboard.append(button_row)

        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    # Собирает InlineKeyboardMarkup из пар (текст, callback) с нужной шириной строки.
    @staticmethod
    def build_kb(
            pairs: Iterable[Tuple[str, str]],
            *,
            row_width: int = 2,
            tail_rows: Sequence[Sequence[Tuple[str, str]]] = (),
    ) -> InlineKeyboardMarkup:
        """
        pairs      – последовательность (text, callback_data)
        row_width  – сколько кнопок в строке
        tail_rows  – список готовых строк, которые надо при-клеить в конец
        """
        kb = InlineKeyboardBuilder()
        for batch in batched(pairs, row_width):
            kb.row(*(InlineKeyboardButton(text=text, callback_data=cb) for text, cb in batch if text))
        for tr in tail_rows:
            kb.row(*(InlineKeyboardButton(text=text, callback_data=cb) for text, cb in tr if text))
        return kb.as_markup()

    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    #   ► Создание клавиатур с указанием параметров
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    # create_invoice() -> create_billing()
    def create_billing(self, link_pay: str, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "💳 Оплатить", "url": link_pay}],
            [{"text": "🔄 Проверить платеж", "callback_data": "check_pay_" + payment_id}],
            [{"text": "🚫 Отменить платеж", "callback_data": "canceled_payment_" + payment_id}],
            [{"text": "🏠 Главное меню", "callback_data": "choose_tariff"}],
        ])

    def cancel_subscription(self, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "⛔️ Отменить подписку", "callback_data": "cancel_subscription_" + payment_id}],
            [{"text": "Назад ↩️", "callback_data": "choose_tariff"}],
        ])

    def verify_invoice(self, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "🔄 Проверить платеж", "callback_data": "check_pay_" + payment_id}],
            [{"text": "🏠 Главное меню", "callback_data": "choose_tariff"}],
        ])

    def save_params(self) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "🚀 Отправить в работу", "callback_data": "task_save"}],
            [{"text": "Назад ↩️", "callback_data": "coefs_confirm"}],
        ])
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    #   ► Создание навигационных клавиатур с указанием параметров
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    # def box_type(
    #         self,
    #         dictionary: dict[int, ...] | None = None,
    #         back: bool = False,
    #         warehouse_id: int = 0,
    #         page: int = 0,
    #         box_default: list[int] = [],
    #         mode: str = ''
    # ) -> InlineKeyboardMarkup:
    #     checked = {5: '🟢 ', 6: '🟢 ', 2: '🟢 '} if dictionary else {}
    #     confirm = (
    #         [InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data="confirm_box_type")]
    #         if dictionary and box_default != dictionary else []
    #     )
    #     back_cb: str = (
    #         f"task_update_select_{warehouse_id}_{page}"
    #         if back else f"task_mode_{mode}"
    #     )
    #
    #     return self.build_inline_keyboard([
    #         [{
    #             "text": f"{checked.get(5, '')}Монопаллеты",
    #             "callback_data": f"box_type_mono_{warehouse_id}_{page}"
    #         }],
    #         [{
    #             "text": f"{checked.get(6, '')}Суперсейф",
    #             "callback_data": f"box_type_safe_{warehouse_id}_{page}"
    #         }],
    #         [{
    #             "text": f"{checked.get(2, '')}Короба",
    #             "callback_data": f"box_type_pan_{warehouse_id}_{page}"
    #         }],
    #         confirm,
    #         [{
    #             "text": "Назад ↩️",
    #             "callback_data": back_cb
    #         }],
    #     ])

    # @staticmethod
    # def coefs(
    #         self,
    #         coef: dict[int, int] | None = None,
    #         back: bool = False,
    #         warehouse_id: int = 0,
    #         page: int = 0,
    #         coef_default: str = ''
    # ) -> InlineKeyboardMarkup:
    #     coef = coef or {}
    #     coef_map: dict[str, str] = {
    #         f"coefs_{i}": "Бесплатные" if i == 0 else f"Коэф. до х{i}" for i in range(21)
    #     }
    #
    #     selected = next((key for key, i in zip(coef_map, range(21)) if i in coef), '')
    #
    #     buttons: list[list[InlineKeyboardButton]] = []
    #     row: list[InlineKeyboardButton] = []
    #
    #     for key, label in coef_map.items():
    #         text = f"{'🟢 ' if key == selected else ''}{label}"
    #         row.append(InlineKeyboardButton(text=text, callback_data=key))
    #         if len(row) == 3:
    #             buttons.append(row)
    #             row = []
    #
    #     if row:
    #         buttons.append(row)
    #
    #     if coef and (selected or str(next(iter(coef), '')) != coef_default):
    #         buttons.append([InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data="confirm_coef")])
    #
    #     back_data = f"task_update_select_{warehouse_id}_{page}" if back else "confirm_selection"
    #     buttons.append([InlineKeyboardButton(text="Назад ↩️", callback_data=back_data)])
    #
    #     return InlineKeyboardMarkup(inline_keyboard=buttons)

    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    #   ► Создание навигационных клавиатур с указанием параметров
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    # 🚛 ⚡ 🎯 📍
    # Выбор складов
    def create_warehouse_list(
            self,
            page_data: ResponseWarehouses,
            selected_warehouses: list[int],
            selected_list: list[int],
            existing_whs_ids: list[int]
    ) -> InlineKeyboardMarkup:
        # --- данные из модели: Парсинг Pydantic модели --------------------------
        warehouses = page_data.warehouses
        page_idx: int = page_data.page_index
        total_pages = page_data.total_pages
        url = f"task_mode_{page_data.mode}"

        # --- основная сетка кнопок ----------------------------------------------
        pairs: list[tuple[str, str]] = []
        for warehouse in warehouses:
            wid = warehouse["id"]
            name = warehouse["name"]

            if wid in existing_whs_ids:
                label = f"🔔 {name}"
                cb_data = f"ignore_wh_{wid}"
            else:
                label = f"🟢 {name}" if wid in (*selected_warehouses, *selected_list) else name
                cb_data = f"{url}_id{wid}"

            pairs.append((label, cb_data))

        # --- «хвост» (пагинация, подтверждение, назад) ---------------------------
        tail_rows: list[list[tuple[str, str]]] = []
        pagination: list[tuple[str, str]] = []

        if page_idx > 0:
            pagination.append(("⬅️ Предыдущая", f"{url}_{page_idx - 1}"))
        if page_idx < total_pages - 1:
            pagination.append(("Следующая ➡️", f"{url}_{page_idx + 1}"))
        if pagination:
            tail_rows.append(pagination)

        if selected_warehouses:
            tail_rows.append([("Подтвердить выбор ✅", f"{url}_confirm")])

        tail_rows.append([("Назад ↩️", "create_task")])

        # --- сборка --------------------------------------------------------------
        return self.build_kb(pairs, row_width=2, tail_rows=tail_rows)

    # 📦 ✅
    # Выбор типов коробок
    def box_type(
            self,
            data: ResponseBoxTypes,
            box_titles: dict[str, str],
            url: str = 'box_type',
            url_back: Optional[str] = None
    ) -> InlineKeyboardMarkup:
        # --- шорткаты и маркеры ----------------------------------------------------
        selected = set(data.selected) or []  # отмеченные типы
        checked = {i: "🟢 " for i in (selected or {})}  # зелёная точка у выбранных
        if url_back is None:
            url_back = f"task_mode_{data.mode}"  # возвращает к выбору складов

        # --- кнопки типов коробок --------------------------------------------------
        pairs: list[tuple[str, str]] = []
        for bt in BoxType:  # Enum обеспечивает фикс. порядок
            title = box_titles[bt]  # "Монопаллеты" / …
            code = bt.value  # "mono" / "safe" / "pan"
            bullet = "🟢 " if code in selected else ""  # зелёная метка
            cb_data = f"{url}_{code}_{data.warehouse_id}_{data.page}"

            pairs.append((f"{bullet}{title}", cb_data))

        # --- хвостовые кнопки (confirm / back / pagination) ------------------------
        tail: list[list[tuple[str, str]]] = []

        # confirm – показываем, если выбор есть и он отличается от дефолта
        # print(set(data.box_default), selected)
        if selected and list(set((data.box_default or []))) != list(selected):
            tail.append([("Подтвердить выбор ✅", f"{url}_confirm")])

        # назад
        back_cb: str = f"task_update_select_{data.warehouse_id}_{data.page}" if data.back else url_back
        tail.append([("Назад ↩️", back_cb)])

        # --- сборка и возврат -------------------------------------------------------
        return self.build_kb(pairs, row_width=1, tail_rows=tail)

    # 🧮 📊
    # Выбор коэффициентов
    def coefs(
            self,
            data: ResponseCoefs,
            url: str = 'coefs',
            url_back: Optional[str] = None
    ) -> InlineKeyboardMarkup:
        # --- шорткаты и маркеры --------------------------------------------------
        selected = data.selected                    # один-единственный int | None
        if url_back is None:
            url_back = f"task_mode_{data.mode}_confirm" # возвращает к выбору box-types

        # --- кнопки коэффициентов (21 шт., по 3 в строке) -----------------------
        pairs: list[tuple[str, str]] = []
        for coef_id, title in COEF_TITLES.items():  # 0 → "Бесплатные", …
            bullet = "🟢 " if coef_id == selected else ""
            cb_data = f"{url}_{coef_id}"
            pairs.append((f"{bullet}{title}", cb_data))

        # --- «хвост» (confirm / back) -------------------------------------------
        tail: list[list[tuple[str, str]]] = []

        # confirm – если выбор есть и он отличается от дефолта
        if selected is not None and data.coef_default != selected:
            tail.append([("Подтвердить выбор ✅", f"{url}_confirm")])

        back_cb = (
            f"task_update_select_{data.warehouse_id}_{data.page}"
            if data.back else url_back
        )
        tail.append([("Назад ↩️", back_cb)])

        # --- сборка клавиатуры ---------------------------------------------------
        return self.build_kb(pairs, row_width=3, tail_rows=tail)

    # 📆 🕑
    # Выбор даты поставки (периода времени)
    def create_select_date(
            self,
            url: str = 'select_date',
            url_back: str = 'box_type_confirm',
            url_calendar: str = 'select_diapason'
    ) -> InlineKeyboardMarkup:
        # --- шорткаты -----------------------------------------------------------
        # f"task_update_select_{warehouse_id}_{page}"

        # --- основные кнопки ----------------------------------------------------
        pairs: list[tuple[str, str]] = [
            ("Сегодня", f"{url}_today"),
            ("Завтра", f"{url}_tomorrow"),
            ("Неделя", f"{url}_week"),
            ("Месяц", f"{url}_month"),
            ("Выбрать на календаре", url_calendar),
        ]

        # --- «хвост» (только кнопка «Назад») ------------------------------------
        tail = [[("Назад ↩️", url_back)]]

        # --- сборка и возврат ----------------------------------------------------
        # row_width=2 → «Сегодня|Завтра», «Неделя|Месяц», «Календарь», «Назад»
        return self.build_kb(pairs, row_width=2, tail_rows=tail)

    def create_alarm_list(
            self,
            page_data: ResponseTasks,
            url: str = 'toggle_alarm',
            prefix_icon: tuple[str, str] = ("🔔", "🔕"),
            alarm_helper_btn: bool = True,
            back: str = 'alarm_setting'
    ) -> InlineKeyboardMarkup:
        # --- данные из модели: Парсинг Pydantic модели --------------------------
        warehouses = page_data.warehouses_names_list
        page: int = page_data.page_index
        total_pages = page_data.total_pages
        alarm_status: dict[int, int] = {item.warehouse_id: item.alarm for item in page_data.tasks}

        # --- основная сетка кнопок (по 2 в ряд) -------------------------------------
        pairs: list[tuple[str, str]] = []
        for warehouse in warehouses:
            wid = warehouse["id"]
            name = warehouse["name"]
            icon = prefix_icon[0] if alarm_status.get(wid) else prefix_icon[1]
            label = f"{icon} {name}"
            pairs.append((label, f"{url}_{wid}_{page}"))

        # --- «хвост» (пагинация + действия + назад) ---------------------------------
        tail_rows: list[list[tuple[str, str]]] = []
        pagination: list[tuple[str, str]] = []

        # мы предусматриваем, что стоит ограничение в 30 складов, поэтому пагинации не требуется:

        # if page > 0:
        #     pagination.append(("⬅️ Предыдущая", f"alarm_edit_{page - 1}"))
        # if page < total_pages - 1:
        #     pagination.append(("Следующая ➡️", f"alarm_edit_{page + 1}"))
        # if pagination:
        #     tail_rows.append(pagination)

        if warehouses and alarm_helper_btn:
            tail_rows.append([("Включить для всех", "alarm_all_on")])
            tail_rows.append([("Отключить для всех", "alarm_all_off")])

        tail_rows.append([("Назад ↩️", back)])

        # --- сборка -----------------------------------------------------------------
        return self.build_kb(pairs, row_width=2, tail_rows=tail_rows)

    # @staticmethod
    # def create_alarm_list(
    #         self,
    #         warehouses: list[dict[str, int | str]],
    #         alarm_status: dict[int, bool],
    #         page: int,
    #         total_pages: int
    # ) -> InlineKeyboardMarkup:
    #     buttons: list[list[InlineKeyboardButton]] = []
    #     row: list[InlineKeyboardButton] = []
    #
    #     for warehouse in warehouses:
    #         wid = warehouse["id"]
    #         name = f"{'🔔' if alarm_status.get(wid) else '🔕'} {warehouse['name']}"
    #         row.append(InlineKeyboardButton(text=name, callback_data=f"toggle_alarm_{wid}_{page}"))
    #
    #         if len(row) == 2:
    #             buttons.append(row)
    #             row = []
    #
    #     if row:
    #         buttons.append(row)
    #
    #     pagination: list[InlineKeyboardButton] = []
    #     if page > 0:
    #         pagination.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"alarm_page_{page - 1}"))
    #     if page < total_pages - 1:
    #         pagination.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"alarm_page_{page + 1}"))
    #     if pagination:
    #         buttons.append(pagination)
    #
    #     if warehouses:
    #         buttons.append([
    #             InlineKeyboardButton(text="Включить для всех", callback_data="alarm_all_on")
    #         ])
    #         buttons.append([
    #             InlineKeyboardButton(text="Отключить для всех", callback_data="alarm_all_off")
    #         ])
    #
    #     buttons.append([InlineKeyboardButton(text="Назад ↩️", callback_data="alarm_setting")])
    #     return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def create_task_list(
            self,
            warehouses: list[dict[str, int | str]],
            alarm_status: dict[int, bool],
            page: int,
            total_pages: int
    ) -> InlineKeyboardMarkup:
        buttons: list[list[InlineKeyboardButton]] = []
        row: list[InlineKeyboardButton] = []

        for warehouse in warehouses:
            wid = warehouse["id"]
            name = str(warehouse["name"])  # Значение alarm никак не влияет на имя
            row.append(InlineKeyboardButton(text=name, callback_data=f"task_update_select_{wid}_{page}"))

            if len(row) == 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        pagination: list[InlineKeyboardButton] = []
        if page > 0:
            pagination.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"task_update_page_{page - 1}"))
        if page < total_pages - 1:
            pagination.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"task_update_page_{page + 1}"))
        if pagination:
            buttons.append(pagination)

        buttons.append([InlineKeyboardButton(text="Назад ↩️", callback_data="my_tasks")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)


    def edit_task_warehouse(
            self,
            warehouse_id: int,
            page: int
    ) -> InlineKeyboardMarkup:
         return self.build_inline_keyboard([
            [{
                "text": "📦 Изменить тип упаковки",
                "callback_data": f"task_update_box_{warehouse_id}_{page}"
            }],
            [{
                "text": "🧮 Изменить коэффициент",
                "callback_data": f"task_update_coef_{warehouse_id}_{page}"
            }],
            [{
                "text": "📅 Изменить период",
                "callback_data": f"task_update_date_{warehouse_id}_{page}"
            }],
            [{
                "text": "🗑️ Удалить задачу",
                "callback_data": f"task_delete_id{warehouse_id}_{page}"
            }],
            [{
                "text": "Назад ↩️",
                "callback_data": f"task_update_page_{page}"
            }],
        ])

    @staticmethod
    def generate_calendar(
        *,
        year: int | None = None,  # выбранный год   (None → текущий)
        month: int | None = None,  # выбранный месяц (None → текущий)
        highlight_day: int | None = None,  # «выбранный» день (None → нет)
        confirm: bool = False,  # показать кнопку «Подтвердить выбор»
        url: str = 'select_day',
        url_confirm: str = 'date_confirm',
        url_back: str = 'coefs_confirm',
        url_change: str = 'change_month'
    ) -> InlineKeyboardMarkup:
        """
        Генерирует инлайн-календарь одного месяца.

        ┌───────────────┐
        │  [Май 2025]   │
        │ Пн Вт Ср Чт … │
        │  1  2  3 ...  │
        │               │
        │ ◀️ Сегодня ▶️ │
        │   Подтвердить │  (если confirm=True)
        │      Назад    │
        └───────────────┘
        """
        # ── 0. дата по умолчанию ------------------------------------------
        today = datetime.now()
        year = year or today.year
        month = month or today.month
        highlight_day = highlight_day or today.day

        # ── 1. заголовок и дни недели -------------------------------------
        # Можно использовать локализованные названия месяцев:
        MONTHS: list[str] = [
            "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
            "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
        ]
        WEEKDAYS: list[str] = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        kb: list[list[InlineKeyboardButton]] = [
            # месяц + год
            [InlineKeyboardButton(text=f"[{MONTHS[month - 1]} {year}]", callback_data="ignore")],
            # шапка дней недели
            [InlineKeyboardButton(text=day, callback_data="ignore") for day in WEEKDAYS],
        ]

        # ── 2. сетка дней ---------------------------------------------------
        for week in calendar.monthcalendar(year, month):
            row: list[InlineKeyboardButton] = []
            for day in week:
                if day == 0:  # пустая ячейка
                    row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
                    continue

                # подсветка «сегодня» или выбранного дня
                mark = "❗" if (
                        day == highlight_day and
                        month == today.month and
                        year == today.year
                ) else ""

                row.append(
                    InlineKeyboardButton(
                        text=f"{mark}{day}{mark}",
                        callback_data=f"{url}_{year}_{month}_{day}"
                    )
                )
            kb.append(row)

        # ── 3. навигация месяц назад / сегодня / месяц вперёд --------------
        # Определение предыдущего и следующего месяца
        prev_m = month - 1 or 12
        next_m = month + 1 if month < 12 else 1
        prev_y = year - 1 if month == 1 else year
        next_y = year + 1 if month == 12 else year

        # Нижний ряд кнопок: назад по месяцу, сегодня, вперёд по месяцу
        kb.append([
            InlineKeyboardButton(text="⬅️", callback_data=f"{url_change}_{prev_y}_{prev_m}"),
            InlineKeyboardButton(
                text="Сегодня",
                callback_data=f"{url}_{today.year}_{today.month}_{today.day}"
            ),
            InlineKeyboardButton(text="➡️", callback_data=f"{url_change}_{next_y}_{next_m}"),
        ])

        # ── 4. confirm / back ----------------------------------------------
        if confirm:
            kb.append([InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data=url_confirm)])

        # Кнопка "Назад"
        kb.append([InlineKeyboardButton(text="Назад ↩️", callback_data=url_back)])

        # ── 5. возврат -------------------------------------------------------
        return InlineKeyboardMarkup(inline_keyboard=kb)

    @staticmethod
    def generate_pagination_keyboard(
            current_page: int,
            total_tasks: int,
            page_size: int = 5,
            callback_data: str = "paginate_",
            base_keyboard: InlineKeyboardMarkup | None = None
    ) -> InlineKeyboardMarkup:
        """
        Генерирует клавиатуру с кнопками пагинации и добавляет их к переданной базовой клавиатуре.

        :param self:
        :param current_page: Текущая страница.
        :param total_tasks: Общее количество задач.
        :param page_size: Количество задач на одной странице.
        :param callback_data: Префикс callback_data для кнопок.
        :param base_keyboard: Существующая клавиатура (InlineKeyboardMarkup) для расширения (опционально).
        :return: InlineKeyboardMarkup с кнопками пагинации.
        """
        # total_pages = ((total_tasks - 1) // page_size + 1) - 1
        total_pages: int = (total_tasks - 1) // page_size

        buttons: list[InlineKeyboardButton] = [
            InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"{callback_data}{current_page - 1}")
            if current_page > 0 else None,
            InlineKeyboardButton(text="Следующая ➡️", callback_data=f"{callback_data}{current_page + 1}")
            if current_page < total_pages else None
        ]
        buttons = [btn for btn in buttons if btn]

        if not base_keyboard:
            base_keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        else:
            base_keyboard.inline_keyboard = [
                row for row in base_keyboard.inline_keyboard
                if all(btn.text not in {"⬅️ Предыдущая", "Следующая ➡️"} for btn in row)
            ]

        if buttons:
            base_keyboard.inline_keyboard.insert(0, buttons)

        return base_keyboard