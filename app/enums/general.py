from enum import Enum, IntEnum


class TaskMode(str, Enum):
    FLEX = 'flex'
    MASS = 'mass'

class TariffOptions(IntEnum):
    FREE     = 3
    TARIFF_1 = 10
    TARIFF_2 = 20
    TARIFF_3 = 30