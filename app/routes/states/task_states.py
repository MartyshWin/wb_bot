from aiogram.fsm.state import StatesGroup, State


class TaskStates(StatesGroup):
    # ───────── блок сбора контекста (warehouse, mode, page …) ─────────
    context_data_choose_wh = State()  # «Выберите склад»
    context_data_choose_box_type = State()  # «Выберите тип короба»
    context_data_choose_coef = State()  # «Выберите коэф»
    context_data_choose_period = State()  # «Выберите период»
    context_data_confirm = State()  # показываем сводку, ждём "Ок"

    # ───────── блок оплаты ─────────
    payments_wait_invoice = State()  # выставлен счёт
    payments_wait_result = State()  # проверяем оплату