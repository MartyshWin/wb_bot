from typing import Final

from app.enums.general import BoxType

BOX_TITLES: Final[dict[BoxType, str]] = {
    BoxType.MONO: "Монопаллеты",
    BoxType.SAFE: "Суперсейф",
    BoxType.PAN:  "Короба",
}