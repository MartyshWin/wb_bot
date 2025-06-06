from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Схема для создания задачи
class TaskCreate(BaseModel):
    user_id: int
    warehouse_id: Optional[int] = None
    box_type_id: int
    coefficient: int
    state: str
    alarm: Optional[int] = None
    date: Optional[datetime] = None
    coef_modified: Optional[int] = None

# Схема для частичного обновления задачи
class TaskUpdate(BaseModel):
    warehouse_id: Optional[int] = None
    box_type_id: Optional[int] = None
    coefficient: Optional[int] = None
    state: Optional[str] = None
    alarm: Optional[int] = None
    date: Optional[datetime] = None
    coef_modified: Optional[int] = None

# Схема для возвращения задачи
class TaskRead(BaseModel):
    id: int
    user_id: int
    warehouse_id: Optional[int] = None
    box_type_id: int
    coefficient: int
    state: str
    alarm: Optional[int] = None
    date: Optional[datetime] = None
    coef_modified: Optional[int] = None
    created_at: datetime
    updated_at: datetime