from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    configuring_connection = State()  # Процесс настройки и получения конфига
    filling_profile = State()  # Сохранение данных профиля (интернет, тариф и т.д.)

    # Неиспользуемые состояния (для примера)
    # choosing_connection_method = State()  # Выбор способа подключения (быстрое/ручное)
    # selecting_tariff = State()            # Выбор тарифа/пакета
    # confirming_details = State()          # Подтверждение деталей перед оплатой
    # waiting_for_payment = State()         # Ожидание оплаты
    # issuing_configuration = State()       # Выдача конфигурации после оплаты
    # feedback_or_done = State()            # Завершающее состояние (фидбэк или завершено)
