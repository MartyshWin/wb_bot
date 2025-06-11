from datetime import datetime, date
from typing import Optional

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base  # Base уже содержит id, created_at, updated_at


class Coefficient(Base):
    __tablename__ = "coefficients"

    warehouse_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True, comment="ID склада, к которому относится коэффициент")
    box_type_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="ID типа коробки")
    coefficient: Mapped[int] = mapped_column(Integer, comment="Коэффициент (целое число)")
    date: Mapped[Optional[date]] = mapped_column(DateTime, nullable=True, comment="Дата (период действия коэффициента)")
    modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="Время последнего изменения коэффициента")
