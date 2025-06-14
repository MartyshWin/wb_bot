# https://github.com/MartyshWin/config_logging.git
import copy
import logging
import logging.config
import traceback

from app.enums.logging import LogLevel
from config.LoggerdictConfig import BASE_LOGGING_CONFIG


class ColoredFormatter(logging.Formatter):
    """
    Конфиг для логирования с поддержкой цветного вывода.
    """
    # Цветовые коды ANSI для уровней логирования
    COLORS: dict[str, str] = {
        "DEBUG": "\033[94m",    # Синий
        "INFO": "\033[92m",     # Зеленый
        "SUCCESS": "\033[96m",  # Ярко-голубой (Добавили новый уровень логирования)
        "WARNING": "\033[93m",  # Желтый
        "ERROR": "\033[91m",    # Красный
        "CRITICAL": "\033[95m"  # Фиолетовый
    }
    TIME_COLOR = FILENAME_COLOR = LINENO_COLOR = "\033[97m"  # Белый
    RESET = "\033[0m"          # Сброс цвета

    def format(self, record: logging.LogRecord) -> str:
        """
        Собирает итоговую строку лога с цветами и «человеческим» расположением
        частей сообщения.

        Алгоритм по шагам
        -----------------
        1. ts   ― дата-время события
           * self.formatTime() берёт formatTime из базового Formatter.
           * self.datefmt задаётся при создании ColoredFormatter
             (у вас это "%Y-%m-%d %H:%M:%S").
           * TIME_COLOR / RESET — ANSI-коды белого текста и сброса цвета.

        2. lvl  ― уровень логирования
           * record.levelname — строка "DEBUG", "INFO", …
           * По levelname достаём цвет из словаря COLORS.
           * Окружая levelname скобками «(INFO)», делаем его более заметным.

        3. file ― откуда пришло сообщение
           * record.filename  — файл, где вызвали логгер.
           * record.lineno    — номер строки.
           * FILENAME_COLOR и LINENO_COLOR тоже белые, чтобы не спорили с lvl.

        4. msg  ― само сообщение
           * record.getMessage() корректно подставит все %-форматные аргументы
             или f-строки, переданные в logger.info(...).
           * Для консистентности красим текст тем же цветом, что и уровень.

        5. exc  ― traceback (если был передан exc_info)
           * traceback.format_exception() превращает кортеж exc_info
             в список строк с переносами.
           * Склеиваем, красим «ошибочным» цветом (красным) и добавляем \n
             перед первым символом, чтобы стек оказался на новой строке.

        6. Возврат
           * Склеиваем всё одним f-string:
             ┌ ts ────────────────────┐
             │ 2025-06-13 22:10:01    │
             └────────────────────────┘
             ---                       ← визуальный разделитель
             (INFO)                    ← lvl
             [main.py:42]              ← файл и строка
             ==                        ← ещё один разделитель
             Заголовок сообщения       ← msg
             \nTraceback … (если есть) ← exc
        """
        ts = f"{self.TIME_COLOR}{self.formatTime(record, self.datefmt)}{self.RESET}" # Форматируем время
        lvl = f"{self.COLORS.get(record.levelname, self.RESET)}({record.levelname}){self.RESET}" # Получаем цвет для уровня логирования
        file = f"[{self.FILENAME_COLOR}{record.filename}{self.RESET}:{self.LINENO_COLOR}{record.lineno}{self.RESET}]" # Форматируем уровень, имя файла и номер строки с цветами
        msg = record.getMessage()
        msg = f"{self.COLORS.get(record.levelname, self.RESET)}{msg}{self.RESET}"

        exc = ""
        if record.exc_info: # Получаем сообщение, учитывая сложные аргументы
            exc_lines = traceback.format_exception(*record.exc_info)
            exc = f"\n{self.COLORS['ERROR']}{''.join(exc_lines).strip()}{self.RESET}"

        return f"{ts} --- {lvl} {file} == {msg}{exc}"


def add_success_level():
    """
    Добавляем новый уровень (SUCCESS) к стандартному модулю logging.
    """
    SUCCESS_LEVEL = 25  # Уровень между INFO (20) и WARNING (30)
    logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, message, args, **kwargs)

    logging.Logger.success = success

def setup_logger(logging_level: LogLevel = LogLevel.DEBUG):
    add_success_level()  # Добавляем уровень SUCCESS
    cfg = copy.deepcopy(BASE_LOGGING_CONFIG)

    # ——— динамически подставляем уровень ———
    # Незабываем изменить уровень в КОНФИГЕ и .ENV
    # От этих двух параметров зависит поведение логгера
    cfg["root"]["level"] = logging_level.value
    cfg["handlers"]["console"]["level"] = logging_level.value

    # ——— при необходимости пишем в файл ———
    # ——— Включение записи логов в файл  ———
    # if log_status:
    #     log_path = logs_dir / "app.log"
    #     log_path.parent.mkdir(parents=True, exist_ok=True)
    #
    #     cfg["handlers"]["file"] = {
    #         "class": "logging.FileHandler",
    #         "filename": str(log_path),
    #         "level": logging_level.value,
    #         "formatter": "colored",
    #     }
    #     cfg["root"]["handlers"].append("file")
    logging.config.dictConfig(cfg)


# Использования уровней логирования (Примеры)
if __name__ == "__main__":
    setup_logger()
    logger = logging.getLogger(__name__)

    logger.debug("Это отладочное сообщение.")
    logger.info("Это информационное сообщение.")
    logger.success("Это сообщение об успехе!")  # Наш добавленный уровень
    logger.warning("Это предупреждение.")
    logger.error("Это сообщение об ошибке.")
    logger.critical("Это критическое сообщение.")