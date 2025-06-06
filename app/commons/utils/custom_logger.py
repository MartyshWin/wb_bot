# https://github.com/MartyshWin/config_logging.git
import logging
import traceback

class ColoredFormatter(logging.Formatter):
    """
    Конфиг для логирования с поддержкой цветного вывода.
    """
    # Цветовые коды ANSI для уровней логирования
    COLORS = {
        "DEBUG": "\033[94m",    # Синий
        "INFO": "\033[92m",     # Зеленый
        "SUCCESS": "\033[96m",  # Ярко-голубой (Добавили новый уровень логирования)
        "WARNING": "\033[93m",  # Желтый
        "ERROR": "\033[91m",    # Красный
        "CRITICAL": "\033[95m"  # Фиолетовый
    }
    TIME_COLOR = "\033[97m"    # Белый
    FILENAME_COLOR = "\033[97m"  # Белый
    LINENO_COLOR = "\033[97m"  # Белый
    RESET = "\033[0m"          # Сброс цвета

    def format(self, record):
        # Форматируем время
        formatted_time = f"{self.TIME_COLOR}{self.formatTime(record, self.datefmt)}{self.RESET}"

        # Получаем цвет для уровня логирования
        level_color = self.COLORS.get(record.levelname, self.RESET)

        # Форматируем уровень, имя файла и номер строки с цветами
        levelname = f"{level_color}({record.levelname}){self.RESET}"
        filename = f"{self.FILENAME_COLOR}{record.filename}{self.RESET}"
        lineno = f"{self.LINENO_COLOR}{record.lineno}{self.RESET}"
        file_info = f"[{filename}:{lineno}]"

        # Получаем сообщение, учитывая сложные аргументы
        if record.args:
            message = record.getMessage()  # Обрабатывает message и args автоматически
        else:
            message = record.msg

        # Добавляем цвет к сообщению
        message = f"{level_color}{message}{self.RESET}"

        # Если это ошибка, добавляем информацию о месте возникновения
        if record.exc_info:
            exception_info = traceback.format_exception(*record.exc_info)
            exception_trace = "".join(exception_info).strip()
            exception_trace = f"{self.COLORS['ERROR']}Traceback (most recent call last):\n{exception_trace}{self.RESET}"
        else:
            exception_trace = ""

        # Формируем итоговое сообщение
        formatted_message = (f"{formatted_time} --- {levelname} {file_info} == {message}\n{exception_trace}").strip()
        return formatted_message


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

def setup_logger():
    """
    Настраивает логгер с цветным выводом.
    """
    add_success_level()  # Добавляем уровень SUCCESS

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Создаем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Настраиваем цветной вывод
    formatter = ColoredFormatter(
        "%(message)s",  # Выводим только сообщение (сформированное вручную в `ColoredFormatter`)
        datefmt="%Y-%m-%d %H:%M:%S"  # Формат даты
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


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