from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base  # Base уже содержит: id, created_at, updated_at


class Warehouse(Base):
    __tablename__ = "warehouses"
    __allow_unmapped__ = True  # чтобы SQLAlchemy не ругался

    # убираем timestamp-поля
    created_at = None
    updated_at = None

    warehouse_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, comment="Внешний ID склада (от маркетплейса)")
    warehouse_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Название склада")
    warehouse_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Полный адрес склада")
    work_schedule: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Часы работы / расписание склада")
    accepts_qr: Mapped[int] = mapped_column(Integer, default=0, comment="Принимает QR-этикетки: 0 = нет, 1 = да")
    modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="Дата последнего изменения карточки склада")
    created: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="Когда склад впервые обнаружен в системе")