from typing import Optional
from datetime import datetime

from sqlalchemy import String, Integer, BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from base import Base  # Предполагается, что Base содержит id и metadata

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, comment="ID пользователя Telegram")
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Имя пользователя Telegram")
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Электронная почта")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="Телефон")
    activity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Последняя активность")
    bot_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="ID cозданного пользователем бота")
    bot_status: Mapped[int] = mapped_column(Integer, comment="Статус взаимодействия с ботом")
