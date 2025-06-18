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
    • первый ответ редактирует исходное сообщение,
      остальные — отправляет новыми.
    """
    try:
        # ── 1. нормализуем вход до списка моделей ──────────────────────
        resp_list: Sequence[ResponseModel] = (
            list(responses)  # Iterable → list[…]
            if isinstance(responses, Iterable)
               and not isinstance(responses, (ResponseModel, str, bytes, dict))
            else [responses]  # одиночный ResponseModel
        )
        if not resp_list:  # пусто → ничего не шлём
            return

        # ── 2. первый ответ → edit_text ───────────────────────────────
        first = resp_list[0]
        if first.popup_text:
            await cq.answer(first.popup_text, show_alert=first.popup_alert)

        # ── 2.1. проверяем клавиатуру ───────────────────────────────
        kb = await resolve_kb(first.kb, inline)
        await cq.message.edit_text(first.text, reply_markup=kb)

        # ── 3. остальные ответы → send_message ────────────────────────
        for resp in resp_list[1:]:
            if resp.popup_text:
                await cq.answer(resp.popup_text, show_alert=resp.popup_alert)

            # ── 3.1. проверяем клавиатуру ───────────────────────────────
            kb = await resolve_kb(resp.kb, inline)
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
    user_lang = cq.from_user.language_code or "unknown"
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