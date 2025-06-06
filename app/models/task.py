from typing import Optional
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from base import Base


class Task(Base):
    __tablename__ = "tasks"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), comment="ID пользователя")
    warehouse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("warehouse_list.warehouse_id"), nullable=True, comment="ID склада")
    box_type_id: Mapped[int] = mapped_column(Integer, comment="ID типа коробки")
    coefficient: Mapped[int] = mapped_column(Integer, comment="Коэффициент")
    state: Mapped[str] = mapped_column(String(50), comment="Состояние задачи")
    alarm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Флаг оповещения")
    date: Mapped[datetime] = mapped_column(DateTime, comment="Дата выполнения")
    coef_modified: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Модифицированный коэффициент (если есть)")
