from typing import Optional
from datetime import datetime

from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Bot(Base):
    __tablename__ = "bots"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True, comment="ID владельца бота")
    bot_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="Уникальный ID бота")
    api_token: Mapped[str] = mapped_column(Text, nullable=False, comment="API токен Telegram Bot")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="Статус активности бота (1 = активен)")
