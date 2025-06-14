from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import logging

from app.commons.responses.task import TaskResponse
from app.keyboards.inline.general import InlineKeyboardHandler

router = Router()
inline = InlineKeyboardHandler()
controller = TaskResponse(inline_handler=inline)


#----------------------------------------#----------------------------------------
# Обработчик кнопки "Создать задачу".
# Перенести всю логику создания задачи в отдельный модуль
#----------------------------------------#----------------------------------------
@router.callback_query(F.data.startswith('create_task'))
async def create_task_handler(callback_query: CallbackQuery, state: FSMContext) -> None | dict:
    try:
        await state.clear()
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

    Примечания:
    - Лимит на одну страницу установлен на 10 складов.
    - Используется округление вверх для подсчёта количества страниц.

    Возвращаемые данные:
    - Обновляет текст сообщения с кнопками для выбора складов.
    """
    try:
        data = callback_query.data.split("_")
        user_lang = callback_query.from_user.language_code or "unknown"

        response = await controller.handle_task_mode(
            callback_query.from_user.id,
            callback_query.from_user.username,
            user_lang,
            data,
            state
        )
        await callback_query.message.edit_text(response.text, reply_markup=response.kb)
    except Exception as e:
        logging.error("message:" + str(e), exc_info=True)


# @router.callback_query(
#     F.state == Order.confirming,         # тот же эффект
#     F.data.startswith("task_mode_")
# )