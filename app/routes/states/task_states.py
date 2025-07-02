from aiogram.fsm.state import StatesGroup, State


class TaskStates(StatesGroup):
    # ───────── блок сбора контекста (warehouse, mode, page …) ─────────
    context_data_setup_task = State()  # «Создание задачи»
    update_task = State()

    # ───────── блок оплаты ─────────
    payments_wait_invoice = State()  # выставлен счёт
    payments_wait_result = State()  # проверяем оплату