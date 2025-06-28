import logging
from typing import Union, Sequence, Iterable

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.keyboards.inline.general import InlineKeyboardHandler
from app.schemas.general import ResponseModel

# тип-подсказка: либо один ResponseModel, либо список
ResponseLike = Union["ResponseModel", Sequence["ResponseModel"]]

# тип-подсказка: либо строковый «псевдоним» клавиатуры, либо готовый объект
KBLike = Union[str, InlineKeyboardMarkup]

async def template_callback(
    cq: CallbackQuery,
    state: FSMContext,
    inline: InlineKeyboardHandler,
    *,
    responses: ResponseLike,
):
    """
    Универсальный обработчик:
    • принимает 1 или несколько ResponseModel;
    • у `ResponseModel.type_edit` два режима:
        - "message"  → `edit_text()` (текст + клавиатура);
        - "keyboard" → `edit_reply_markup()` (только клавиатура).
      По умолчанию "message".
    • первый ответ редактирует исходное сообщение,
      остальные — отправляет новыми.
    """
    try:
        # ── 1. нормализуем вход до списка моделей ──────────────────────
        resp_list: list[ResponseModel]
        if isinstance(responses, ResponseModel):
            resp_list = [responses] # одиночный ResponseModel
        elif isinstance(responses, Iterable):
            resp_list = [r for r in responses if r is not None]
            if not all(isinstance(r, ResponseModel) for r in resp_list):
                raise TypeError("template_callback: ожидался ResponseModel")
        else:
            raise TypeError(f"template_callback: unsupported type {type(responses)!r}")

        if not resp_list:  # пусто → ничего не шлём
            return

        # ── 3. первый ответ → edit_text ───────────────────────────────
        first = resp_list[0]
        kb = None
        if not first.kb is None:
            kb: InlineKeyboardMarkup | None = await resolve_kb(first.kb, inline)

        # ── 3.1. если popup (first) → показываем его ──────────────────────────────
        if first.popup_text:
            await cq.answer(first.popup_text, show_alert=first.popup_alert)
        # -----------------------------

        if first.type_edit == "keyboard":  # только поменять КБ
            await cq.message.edit_reply_markup(reply_markup=kb)
        else:  # полное редактирование
            await cq.message.edit_text(first.text, reply_markup=kb)

        # ── 4. остальные ответы → новые сообщения -----------------------------
        for resp in resp_list[1:]:
            kb = None
            if not resp.kb is None:
                kb = await resolve_kb(resp.kb, inline)

            # ── 4.1. если popup (other) → показываем его ──────────────────────────────
            if resp.popup_text:
                await cq.answer(resp.popup_text, show_alert=resp.popup_alert)

            # если нужно редактировать КБ предыдущего сообщения,
            # а не создавать новое – проверяем type_edit
            if resp.type_edit == "keyboard":
                await cq.message.edit_reply_markup(reply_markup=kb)
            else:
                await cq.message.answer(resp.text, reply_markup=kb)
    except Exception as e:
        logging.error(f"template_callback error: {e}", exc_info=True)


async def parse_cq(cq: CallbackQuery):
    """
    Возвращает:
    • data       – список токенов callback-данных (split("_"))
    • user_lang  – язык пользователя или 'unknown'
    """
    data = cq.data.split("_")
    user_lang = cq.from_user.language_code or "ru" # or "unknown"
    return data, user_lang

async def resolve_kb(kb_like: KBLike, inline: InlineKeyboardHandler) -> InlineKeyboardMarkup:
    """
    Приводит «что-угодно-похожее-на-клавиатуру» к реальному объекту
    `InlineKeyboardMarkup`.

    Параметры
    ----------
    kb_like : str | InlineKeyboardMarkup
        • str – псевдоним/выражение: будет передан в `inline.get_keyboard`;
        • InlineKeyboardMarkup – уже готовый объект.

    Возврат
    -------
    InlineKeyboardMarkup
        Гарантированно валидная клавиатура для отправки/редактирования
        сообщения.

    kb = await resolve_kb(some_keyboard)   # some_keyboard: str | InlineKeyboardMarkup
    await callback_query.message.edit_reply_markup(kb)
    """
    # строка → строим по фабрике
    if isinstance(kb_like, str):
        return inline.get_keyboard(kb_like)

    # уже готовая клавиатура → вернуть как есть
    if isinstance(kb_like, InlineKeyboardMarkup):
        return kb_like

    # всё остальное считаем ошибкой разработки
    raise TypeError(f"Не могу преобразовать {kb_like!r} к InlineKeyboardMarkup")