from typing import Final

from app.enums.general import BoxType

BOX_TITLES: Final[dict[BoxType, str]] = {
    BoxType.MONO: "Монопаллеты",
    BoxType.SAFE: "Суперсейф",
    BoxType.PAN:  "Короба",
}

COEF_TITLES: Final[dict[int, str]] = {
    0:  "Бесплатные",
    **{i: f"Коэф. до х{i}" for i in range(1, 21)},   # 1‥20
}