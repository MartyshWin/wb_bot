from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.task import TaskResponse
from app.commons.utils.template_callback import parse_cq, template_callback
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
inline = InlineKeyboardHandler()
controller = TaskResponse(inline_handler=inline)


#----------------------------------------#----------------------------------------
# Обработчик кнопки "Создать задачу".
# Перенести всю логику создания задачи в отдельный модуль
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('create_task'))
async def create_task_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    data, user_lang = await parse_cq(callback_query)

    response = await controller.handle_create_task(
        callback_query,
        user_lang,
        data
    )

    await template_callback(
        callback_query, state, inline,
        responses=response
    )


@router.callback_query(F.data.startswith('task_mode_'))
async def task_mode(callback_query: CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор массовой или гибкой настройки задач.

    Функция устанавливает состояние выбора складов.
    Она загружает первые 10 складов из базы данных, рассчитывает общее количество страниц для пагинации
    и отображает интерфейс с кнопками выбора.

    Примечания:
    - Лимит на одну страницу установлен на 10 складов.
    - Используется округление вверх для подсчёта количества страниц.

    Возвращаемые данные:
    - Обновляет текст сообщения с кнопками для выбора складов.
    """
    data, user_lang = await parse_cq(callback_query)

    response = await controller.handle_task_mode(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(
        callback_query, state, inline,
        responses=response
    )


@router.callback_query(F.data.startswith('box_type_'))
async def box_type(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)

    response = await controller.handle_box_type(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(
        callback_query, state, inline,
        responses=response
    )


@router.callback_query(F.data.startswith('coefs_'))
async def coefs(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)

    response = await controller.handle_coefs(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(
        callback_query, state, inline,
        responses=response
    )


@router.callback_query(F.data.startswith('select_date_'))
async def select_date(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)

    response = await controller.handle_date(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(
        callback_query, state, inline,
        responses=response
    )

#----------------------------------------#----------------------------------------
# Обрабатывает нажатие на кнопку установки диапазона дат
#----------------------------------------#----------------------------------------
@router.callback_query(
    F.data.startswith(('select_diapason',
                       'change_month_',
                       'select_day_',
                       'date_confirm'))
)
async def multi_handler(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)

    response = await controller.handle_date(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(
        callback_query, state, inline,
        responses=response
    )

@router.callback_query(F.data.startswith('task_save'))
async def select_date(callback_query: CallbackQuery, state: FSMContext):
    data, user_lang = await parse_cq(callback_query)

    response = await controller.create_tasks_from_range(
        callback_query,
        user_lang,
        data,
        state
    )
    await template_callback(
        callback_query, state, inline,
        responses=response
    )



# @router.callback_query(
#     F.state == Order.confirming,         # тот же эффект
#     F.data.startswith("task_mode_")
# )