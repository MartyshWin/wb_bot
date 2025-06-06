from .custom_logger import setup_logger as logger  # noqa

# Экспорт всех маршрутов для подключения в приложении
__all__ = [
    "logger"
]
