from datetime import date, datetime
from typing import Optional

def to_date(val: str | date) -> date:
    return val if isinstance(val, date) else datetime.strptime(val, "%Y-%m-%d").date()

def validate_diapason(
        picked_date: date,
        period_start: Optional[str | date],
        period_end: Optional[str | date],
        error: dict[str, str],
        today: Optional[date] = None
) -> tuple[bool, Optional[str]]:
    """Проверка выбранной даты на допустимость."""
    today = today or date.today()

    if picked_date < today or picked_date.year > today.year + 20:
        return False, error['invalid_date']

    if ps := period_start:
        ps = to_date(ps)
        if ps > picked_date:
            return False, error['end_before_start']

    if (ps := period_start) and (pe := period_end):
        ps, pe = to_date(ps), to_date(pe)
        return False, error['already_selected']

    return True, None