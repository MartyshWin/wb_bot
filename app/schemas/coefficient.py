from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Схема для создания строки в таблице `coefficients`.
class CoefficientCreate(BaseModel):
    # Неактивно, так как нельзя создать коэффициенты через бота

    # warehouse_id: Optional[int] = None
    # box_type_id: Optional[int] = None
    # coefficient: int
    # date: Optional[datetime] = None          # дата, к которой относится коэффициент
    # modified: Optional[datetime] = None      # когда коэффициент был пересчитан / изменён
    pass

# Схема для частичного обновления строки `coefficients`.
class CoefficientUpdate(BaseModel):
    # Неактивно, так как нельзя обновлять коэффициенты через бота

    # warehouse_id: Optional[int] = None
    # box_type_id: Optional[int] = None
    # coefficient: Optional[int] = None
    # date: Optional[datetime] = None
    # modified: Optional[datetime] = None
    pass

class CoefficientRead(BaseModel):
    id: int
    warehouse_id: Optional[int] = None
    box_type_id: Optional[int] = None
    coefficient: int
    date: Optional[datetime] = None
    modified: Optional[datetime] = None
