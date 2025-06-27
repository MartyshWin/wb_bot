from datetime import timedelta
from dateutil.relativedelta import relativedelta

from typing import Final

from app.enums.general import BoxType

BOX_TITLES: Final[dict[BoxType, str]] = {
    BoxType.MONO: "Монопаллеты",
    BoxType.SAFE: "Суперсейф",
    BoxType.PAN:  "Короба",
}

BOX_TYPE_MAP: Final[dict[str, int]] = {
    "mono": 5,
    "safe": 6,
    "pan": 2,
}

BOX_TITLES_RU: Final[dict[int, str]] = {
    2: "Короба",
    5: "Монопаллеты",
    6: "Суперсейф",
}

COEF_TITLES: Final[dict[int, str]] = {
    0:  "Бесплатные",
    **{i: f"Коэф. до х{i}" for i in range(1, 21)},   # 1‥20
}

PERIOD_MAP = {
    "today":    lambda d: (d, d),
    "tomorrow": lambda d: (d + timedelta(days=1),) * 2,
    "week":     lambda d: (d, d + timedelta(weeks=1)),
    "month":    lambda d: (d, d + relativedelta(months=1)),
}