from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    configuring_connection = State()  # Процесс настройки и получения конфига
    filling_profile = State()  # Сохранение дан
