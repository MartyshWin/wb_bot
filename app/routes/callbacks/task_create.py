from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.task import TaskResponse
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
controller = TaskResponse()
inline = InlineKeyboardHandler()

#----------------------------------------#----------------------------------------
# Обработчик кнопки "Создать задачу".
# Перенести всю логику создания задачи в отдельный модуль
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('create_task'))
async def create_task_handler(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    try:
        data = callback_query.data.split("_")
        user_lang = callback_query.from_user.language_code or "unknown"

        response = await controller.handle_create_task(
            callback_query.from_user.id,
            callback_query.from_user.username,
            user_lang,
            data
        )

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e), exc_info=True)

@router.callback_query(F.data.startswith('task_mode_'))
async def task_mode(callback_query: CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор массовой или гибкой настройки задач.

    Функция устанавливает состояние выбора складов.
    Она загружает первые 10 складов из базы данных, рассчитывает общее количество страниц для пагинации
    и отображает интерфейс с кнопками выбора.

    Логика работы:
    1. Устанавливает состояние FSMContext на `context_data`.
    2. Инициализирует данные в FSMContext:
       - `current_page`: Номер текущей страницы (изначально 0).
       - `list`: Список ID выбранных складов (изначально пустой).
       - `box_type`: Список выбранных типов коробок (изначально пустой).
       - `coefs`: Выбранный коэффициент (изначально пустой).
    3. Загружает данные первых 10 складов.
    4. Рассчитывает общее количество страниц с помощью округления вверх.
    5. Создаёт интерфейс с кнопками выбора складов.
    6. Обновляет текст сообщения и добавляет кнопки в интерфейс.

    Параметры:
    - callback_query (CallbackQuery): Объект, содержащий данные о взаимодействии пользователя с кнопкой.
    - state (FSMContext): Контекст состояния FSM для хранения текущих данных.

    Используемые методы:
    - `App.get_warehouses(offset, limit)`: Загружает данные складов из базы данных.
    - `App.get_total_warehouses()`: Получает общее количество складов.
    - `inline.create_warehouse_list(warehouses, mode, context_data, page, total_pages)`:
      Создаёт кнопки выбора складов с учётом пагинации и текущего состояния.

    Словарь текстов:
    - "Выберите склады, которые хотите настроить": Основной текст для интерфейса.

    Примечания:
    - Лимит на одну страницу установлен на 10 складов.
    - Используется округление вверх для подсчёта количества страниц.

    Возвращаемые данные:
    - Обновляет текст сообщения с кнопками для выбора складов.
    """
    _, _, mode = callback_query.data.split("_")


    selected_list = App.get_tasks_with_unique_warehouses(callback_query.from_user.id)
    task_setup = {'current_page': 0, 'list': [], 'selected_list': selected_list, 'box_type': [], 'coefs': '',
                  'period_start': '', 'period_end': '', 'mode': mode}
    # Установка состояния и начальных данных

    state_data = await state.get_data()
    context_data = state_data.get('context_data')

    if not context_data or context_data.get('mode') != mode:
        await state.clear()
        await state.set_state(TaskStates.context_data)
        await state.update_data(context_data=task_setup)
        setup_list = []
    else:
        setup_list = context_data['list']

    # Получение данных складов и создание кнопок
    limit, offset = 30, 0
    warehouses = App.get_warehouses(offset, limit)
    total_pages = -(-App.get_total_warehouses() // limit)  # Округление вверх

    text = App.lang_dict['create_task_list']['task_mode_mass'] if mode == "mass" else \
    App.lang_dict['create_task_list']['task_mode_flex']

    # context_data['list'].remove(warehouse_id) if warehouse_id in context_data['list'] else \
    # context_data['list'].append(warehouse_id)
    # Генерация интерфейса
    warehouse_buttons = inline.create_warehouse_list(warehouses, mode, setup_list, selected_list, offset,
                                                     total_pages)
    # Обновление сообщения
    await callback_query.message.edit_text(text, reply_markup=warehouse_buttons)

    # ----------------------------------------
    try:
        data = callback_query.data.split("_")
        user_lang = callback_query.from_user.language_code or "unknown"

        response = await controller.handle_task_mode(
            callback_query.from_user.id,
            callback_query.from_user.username,
            user_lang,
            mode
        )

        await callback_query.message.edit_text(response.text, reply_markup=inline.get_keyboard(response.kb))
    except Exception as e:
        logging.error("message:" + str(e), exc_info=True)
