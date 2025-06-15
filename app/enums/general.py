from enum import Enum, IntEnum


class TaskMode(str, Enum):
    FLEX = 'flex'
    MASS = 'mass'

class BoxType(str, Enum):
    MONO = 'mono'   # Монопаллеты
    SAFE = 'safe'   # Суперсейф
    PAN = 'pan'     # Короба

class TariffOptions(IntEnum):
    FREE     = 3
    TARIFF_1 = 10
    TARIFF_2 = 20
    TARIFF_3 = 30