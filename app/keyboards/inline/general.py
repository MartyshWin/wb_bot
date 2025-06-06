import re
from typing import Union, Callable, List, Any, TypedDict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import datetime

# Кнопки должны получать язык приложения, чтобы соответствовать выбранному пользователем
class InlineKeyboardHandler:
    def __init__(self):

        self.start_kb: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "📝 Создать список задач", "callback_data": "create_task"}],
            [{"text": "🗂 Мой список задач", "callback_data": "my_tasks"}],
            [{"text": "⚙️ Настройка уведомлений", "callback_data": "alarm_setting"}],
            [{"text": "💎 Подписка", "callback_data": "choose_tariff"}],
            [{"text": "ℹ️ Инструкция", "callback_data": "select_diapason"}],
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
            [{"text": "Да", "callback_data": "tasks_update_all"}],
            [{"text": "Отмена", "callback_data": "main"}],
        ])

        self.search_slot_mass: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "🚀 Отправить в работу", "callback_data": "task_save"}],
            [{"text": "🏠 Главное меню", "callback_data": "main"}],
        ])

        self.search_slot_flex: InlineKeyboardMarkup = self.build_inline_keyboard([
            [{"text": "🚀 Отправить в работу", "callback_data": "task_save"}],
            [{"text": "🏠 Главное меню", "callback_data": "main"}],
        ])

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

        # self.select_date: InlineKeyboardMarkup = self.create_select_date()


    @staticmethod
    # Создать enums модель для method, где ожидается fast или full
    def get_continue_kb(method: str) -> InlineKeyboardMarkup:
        """
        Создает inline-клавиатуру с кнопкой "Продолжить" и параметризованным callback_data.

        :param method: Метод подключения, например "fast" или "full".
                      Используется для передачи в callback_data и последующей обработки.
        :return: Объект InlineKeyboardMarkup с двумя кнопками:
                 - "Продолжить", содержащая callback_data вида "continue_setup:<method>"
                 - "Назад", ведущая на начальное меню с callback_data "home"
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Продолжить", callback_data=f"continue_setup:{method}")],
                [InlineKeyboardButton(text="◀️ Назад", callback_data="home")],
            ]
        )


    def get_keyboard(self, attribute_name: str | object) -> str | None | Any:
        """
        Получает метод по имени и вызывает его с аргументами, если они указаны.

        :param attribute_name: Имя метода и аргументы в формате 'method_name(arg1, arg2)'.
        :return: Результат выполнения метода или строка с ошибкой, если метод не найден.
        """
        # Проверяем, есть ли скобки в строке
        if attribute_name is not None:
            if '(' in attribute_name and attribute_name.endswith(')'):
                # Извлекаем имя метода и аргументы
                match = re.match(r"(\w+)\((.*)\)", attribute_name)
                if not match:
                    return "Invalid format"

                method_name, args_str = match.groups()

                # Получаем метод по имени
                method = getattr(self, method_name, None)
                if not method or not callable(method):
                    return "Not Found keyboard"

                # Разделяем аргументы по запятой и убираем лишние пробелы
                args: List[str] = [arg.strip() for arg in args_str.split(',')] if args_str else []

                # Вызываем метод с аргументами
                return method(*args)
            else:
                # Если скобок нет, просто вызываем метод без аргументов
                return getattr(self, attribute_name, "Not Found keyboard")

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

    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    #   ► Создание клавиатур с указанием параметров
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    @staticmethod
    # create_invoice() -> create_billing()
    def create_billing(self, link_pay: str, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "💳 Оплатить", "url": link_pay}],
            [{"text": "🔄 Проверить платеж", "callback_data": "check_pay_" + payment_id}],
            [{"text": "🚫 Отменить платеж", "callback_data": "canceled_payment_" + payment_id}],
            [{"text": "🏠 Главное меню", "callback_data": "choose_tariff"}],
        ])

    @staticmethod
    def cancel_subscription(self, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "⛔️ Отменить подписку", "callback_data": "cancel_subscription_" + payment_id}],
            [{"text": "Назад ↩️", "callback_data": "choose_tariff"}],
        ])

    @staticmethod
    def verify_invoice(self, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "🔄 Проверить платеж", "callback_data": "check_pay_" + payment_id}],
            [{"text": "🏠 Главное меню", "callback_data": "choose_tariff"}],
        ])

    @staticmethod
    def save_params(self, payment_id: str) -> InlineKeyboardMarkup:
        return self.build_inline_keyboard([
            [{"text": "🚀 Отправить в работу", "callback_data": "task_save"}],
            [{"text": "Назад ↩️", "callback_data": "select_diapason_back"}],
        ])
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    #   ► Создание навигационных клавиатур с указанием параметров
    # 〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰
    def box_type(
            self,
            dictionary: dict[int, ...] | None = None,
            back: bool = False,
            warehouse_id: int = 0,
            page: int = 0,
            box_default: list[int] = [],
            mode: str = ''
    ) -> InlineKeyboardMarkup:
        checked = {5: '🟢 ', 6: '🟢 ', 2: '🟢 '} if dictionary else {}
        confirm = (
            [InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data="confirm_box_type")]
            if dictionary and box_default != dictionary else []
        )
        back_cb: str = (
            f"task_update_select_{warehouse_id}_{page}"
            if back else f"task_mode_{mode}"
        )

        return self.build_inline_keyboard([
            [{
                "text": f"{checked.get(5, '')}Монопаллеты",
                "callback_data": f"box_type_mono_{warehouse_id}_{page}"
            }],
            [{
                "text": f"{checked.get(6, '')}Суперсейф",
                "callback_data": f"box_type_safe_{warehouse_id}_{page}"
            }],
            [{
                "text": f"{checked.get(2, '')}Короба",
                "callback_data": f"box_type_pan_{warehouse_id}_{page}"
            }],
            confirm,
            [{
                "text": "Назад ↩️",
                "callback_data": back_cb
            }],
        ])

    @staticmethod
    def coefs(
            self,
            coef: dict[int, int] | None = None,
            back: bool = False,
            warehouse_id: int = 0,
            page: int = 0,
            coef_default: str = ''
    ) -> InlineKeyboardMarkup:
        coef = coef or {}
        coef_map: dict[str, str] = {
            f"coefs_{i}": "Бесплатные" if i == 0 else f"Коэф. до х{i}" for i in range(21)
        }

        selected = next((key for key, i in zip(coef_map, range(21)) if i in coef), '')

        buttons: list[list[InlineKeyboardButton]] = []
        row: list[InlineKeyboardButton] = []

        for key, label in coef_map.items():
            text = f"{'🟢 ' if key == selected else ''}{label}"
            row.append(InlineKeyboardButton(text=text, callback_data=key))
            if len(row) == 3:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        if coef and (selected or str(next(iter(coef), '')) != coef_default):
            buttons.append([InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data="confirm_coef")])

        back_data = f"task_update_select_{warehouse_id}_{page}" if back else "confirm_selection"
        buttons.append([InlineKeyboardButton(text="Назад ↩️", callback_data=back_data)])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def create_warehouse_list(
            self,
            warehouses: list[dict[str, int | str]],
            mode: str,
            selected_warehouses: list[int],
            selected_list: list[int],
            page: int,
            total_pages: int
    ) -> InlineKeyboardMarkup:
        buttons: list[list[InlineKeyboardButton]] = []
        row: list[InlineKeyboardButton] = []

        for warehouse in warehouses:
            name = str(warehouse["name"])
            wid = warehouse["id"]
            if wid in selected_warehouses or wid in selected_list:
                name = f"🟢 {name}"

            row.append(InlineKeyboardButton(text=name, callback_data=f"select_warehouse_{mode}_{wid}"))
            if len(row) == 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        pagination: list[InlineKeyboardButton] = []
        if page > 0:
            pagination.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"warehouse_page_{mode}_{page - 1}"))
        if page < total_pages - 1:
            pagination.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"warehouse_page_{mode}_{page + 1}"))
        if pagination:
            buttons.append(pagination)

        if selected_warehouses:
            buttons.append([InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data="confirm_selection")])

        buttons.append([InlineKeyboardButton(text="Назад ↩️", callback_data="tasks_append")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def create_alarm_list(
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
            name = f"{'🔔' if alarm_status.get(wid) else '🔕'} {warehouse['name']}"
            row.append(InlineKeyboardButton(text=name, callback_data=f"toggle_alarm_{wid}_{page}"))

            if len(row) == 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        pagination: list[InlineKeyboardButton] = []
        if page > 0:
            pagination.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"alarm_page_{page - 1}"))
        if page < total_pages - 1:
            pagination.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"alarm_page_{page + 1}"))
        if pagination:
            buttons.append(pagination)

        if warehouses:
            buttons.append([
                InlineKeyboardButton(text="Включить для всех", callback_data="alarm_all_on")
            ])
            buttons.append([
                InlineKeyboardButton(text="Отключить для всех", callback_data="alarm_all_off")
            ])

        buttons.append([InlineKeyboardButton(text="Назад ↩️", callback_data="alarm_setting")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

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
                "text": "Изменить тип упаковки",
                "callback_data": f"task_update_box_{warehouse_id}_{page}"
            }],
            [{
                "text": "Изменить коэффициент",
                "callback_data": f"task_update_coef_{warehouse_id}_{page}"
            }],
            [{
                "text": "Изменить период",
                "callback_data": f"task_update_date_{warehouse_id}_{page}"
            }],
            [{
                "text": "Удалить задачу",
                "callback_data": f"task_delete_{warehouse_id}_{page}"
            }],
            [{
                "text": "Назад ↩️",
                "callback_data": f"task_update_page_{page}"
            }],
        ])

    @staticmethod
    def generate_calendar(
            self,
            selected_year: int | None = None,
            selected_month: int | None = None,
            selected_day: int | None = None,
            status_end: bool = False
    ) -> InlineKeyboardMarkup:
        if selected_year is None:
            selected_year = datetime.now().year
        if selected_month is None:
            selected_month = datetime.now().month

        # Можно использовать локализованные названия месяцев:
        month_names: list[str] = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                       "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        days_of_week: list[str] = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        month_name: str = month_names[selected_month - 1]

        inline_keyboard: list[list[InlineKeyboardButton]] = [
            [# Заголовок (Месяц Год)
                InlineKeyboardButton(text=f"[{month_name} {selected_year}]", callback_data="ignore")
            ],
            [  # Дни недели
                InlineKeyboardButton(text=day, callback_data="ignore") for day in days_of_week
            ]
        ]

        # Календарь месяца
        month_calendar = calendar.monthcalendar(selected_year, selected_month)
        for week in month_calendar:
            row = []
            for day in week:
                if day == 0:
                    row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
                else:
                    if day == datetime.now().day and selected_month == datetime.now().month and selected_year == datetime.now().year:
                        row.append(
                            InlineKeyboardButton(
                                text=f"❗{str(day)}❗️",
                                callback_data=f"select_day_{selected_year}_{selected_month}_{day}"
                            )
                        )
                    else:
                        row.append(
                            InlineKeyboardButton(
                                text=str(day),
                                callback_data=f"select_day_{selected_year}_{selected_month}_{day}"
                            )
                        )
            inline_keyboard.append(row)

        # Определение предыдущего и следующего месяца
        prev_month = selected_month - 1 if selected_month > 1 else 12
        next_month = selected_month + 1 if selected_month < 12 else 1
        prev_year = selected_year if selected_month > 1 else selected_year - 1
        next_year = selected_year if selected_month < 12 else selected_year + 1

        # Нижний ряд кнопок: назад по месяцу, сегодня, вперёд по месяцу
        inline_keyboard.append([
            InlineKeyboardButton(
                text="⬅️", callback_data=f"change_month_{prev_year}_{prev_month}"
            ),
            InlineKeyboardButton(
                text="Сегодня",
                callback_data=f"select_day_{datetime.now().year}_{datetime.now().month}_{datetime.now().day}"
            ),
            InlineKeyboardButton(
                text="➡️", callback_data=f"change_month_{next_year}_{next_month}"
            )
        ])

        if status_end:
            # Кнопка "Подтвердить выбор"
            inline_keyboard.append([
                InlineKeyboardButton(text="Подтвердить выбор ✅", callback_data="confirm_date")
            ])

        # Кнопка "Назад"
        inline_keyboard.append([
            InlineKeyboardButton(text="Назад ↩️", callback_data="confirm_coef")
        ])

        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    def create_select_date(
            self,
            back: bool = False,
            warehouse_id: int = 0,
            page: int = 0
    ) -> InlineKeyboardMarkup:
        back_cb: str = (
            f"task_update_select_{warehouse_id}_{page}"
            if back else "confirm_box_type"
        )

        return self.build_inline_keyboard([
            [
                {"text": "Сегодня", "callback_data": "select_date_today"},
                {"text": "Завтра", "callback_data": "select_date_tomorrow"},
            ],
            [
                {"text": "Неделя", "callback_data": "select_date_week"},
                {"text": "Месяц", "callback_data": "select_date_month"},
            ],
            [{"text": "Выбрать на календаре", "callback_data": "select_diapason"}],
            [
                {"text": "Назад ↩️", "callback_data": back_cb},
            ],
        ])

    @staticmethod
    def generate_pagination_keyboard(
            self,
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