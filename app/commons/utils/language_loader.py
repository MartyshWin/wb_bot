import importlib
from types import ModuleType

from app.schemas.typed_dict import LangType


def load_language(lang_code: str) -> LangType:
    """
    Загружает словарь языка по коду языка (например, 'ru', 'en').

    :param lang_code: Код языка, например 'ru' или 'en'
    :return: Словарь переводов
    """
    try:
        # print(f"app.localization.{lang_code}")
        module: ModuleType = importlib.import_module(f"app.localization.{lang_code}")
        return getattr(module, "lang", {})
    except ModuleNotFoundError:
        # Фоллбек на английский язык
        fallback_module: ModuleType = importlib.import_module("app.localization.en")
        return getattr(fallback_module, "lang", {})