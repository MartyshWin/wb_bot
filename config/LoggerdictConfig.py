BASE_LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,

    # ---------- FORMATTERS ----------
    "formatters": {
        "colored": {
            "()": "app.commons.utils.custom_logger.ColoredFormatter",     # указываем путь до стандартного ColoredFormatter
            "fmt": "%(message)s",                 # сам текст формата не нужен — ColoredFormatter переопределит
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    # ---------- HANDLERS ----------
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored",
        },
    },

    # ---------- ЛОГГЕРЫ ПО МОДУЛЯМ ----------
    "loggers": {
        # заглушаем SQLAlchemy: BEGIN/COMMIT не увидим, ошибки остаются
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },

    # ---------- КОРНЕВОЙ ЛОГГЕР ----------
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}