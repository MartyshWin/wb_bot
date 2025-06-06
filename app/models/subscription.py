from typing import Optional
from datetime import datetime, date

from sqlalchemy import String, Integer, Date, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), comment="ID пользователя")
    payment_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="ID платежа")
    tarif: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Название тарифа")
    amount: Mapped[float] = mapped_column(Float, comment="Сумма оплаты")
    period: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="Период действия подписки")
    free_sub: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0, comment="Признак бесплатной подписки")
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="unpaid", comment="Статус подписки")
