from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base_schema import BaseSchema


#----------------------------------------#----------------------------------------
# Warehouse – Pydantic-схемы
#----------------------------------------#----------------------------------------

# Схема для создания строки в таблице `warehouses`.
class WarehouseCreate(BaseModel):
    # Неактивно, так как нельзя создавать склады

    # warehouse_id: int
    # warehouse_name: str
    # warehouse_address: Optional[str] = None
    # work_schedule: Optional[str] = None
    # accepts_qr: int = 0                       # 0 = не принимает, 1 = принимает
    # created: Optional[datetime] = None        # если не задаётся – БД выставит сама
    # modified: Optional[datetime] = None       # для первичного создания можно опустить
    pass

# Схема для частичного обновления информации о складе.
class WarehouseUpdate(BaseModel):
    # Неактивно, так как нельзя обновлять существующие склады

    # warehouse_name: Optional[str] = None
    # warehouse_address: Optional[str] = None
    # work_schedule: Optional[str] = None
    # accepts_qr: Optional[int] = None
    # modified: Optional[datetime] = None
    pass

# Схема для отдачи наружу (read-only).
class WarehouseRead(BaseSchema):
    id: int
    warehouse_id: int
    warehouse_name: str
    warehouse_address: Optional[str] = None
    work_schedule: Optional[str] = None
    accepts_qr: int
    created: Optional[datetime] = None
    modified: Optional[datetime] = None

# Полная внутренняя схема (все поля, включая метаданные).
class WarehouseSchema(BaseModel):
    id: int
    warehouse_id: int
    warehouse_name: str
    warehouse_address: Optional[str] = None
    work_schedule: Optional[str] = None
    accepts_qr: int = 0
    created: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
