from typing import Optional
from datetime import datetime

from sqlalchemy import String, Integer, BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from base import Base  # Предполагается, что Base содержит id и metadata

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    activity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bot_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bot_status: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
