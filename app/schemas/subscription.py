from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


#----------------------------------------#----------------------------------------
# Subscription – Pydantic-схемы
#----------------------------------------#----------------------------------------

# Схема для создания новой подписки.
class SubscriptionCreate(BaseModel):
    user_id: int
    payment_id: Optional[str] = None
    tarif: str                               # название тарифа (basic / pro / …)
    amount: float                            # стоимость
    period: Optional[date] = None            # дата окончания (если фиксирована)
    free_sub: int = 0                        # 0 = обычная, 1 = бесплатная пробная
    status: str = "unpaid"                   # unpaid / active / expired / …

# Схема для частичного обновления подписки.
class SubscriptionUpdate(BaseModel):
    payment_id: Optional[str] = None
    tarif: Optional[str] = None
    amount: Optional[float] = None
    period: Optional[date] = None
    free_sub: Optional[int] = None
    status: Optional[str] = None

# Схема для отдачи данных наружу (read-only).
class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    payment_id: Optional[str] = None
    tarif: str
    amount: float
    period: Optional[date] = None
    free_sub: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Полная схема (для внутреннего использования).
class SubscriptionSchema(BaseModel):
    id: int
    user_id: int
    payment_id: Optional[str] = None
    tarif: str
    amount: float
    period: Optional[date] = None
    free_sub: int = 0
    status: str = "unpaid"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
