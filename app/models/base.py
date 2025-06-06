from datetime import datetime, UTC, timezone

from sqlalchemy import MetaData, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config.config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    # Настройки метаданных для всей базы
    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='Event ID - PK'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc).replace(tzinfo=None),
        comment = 'Post creation date' # Дата создания
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        comment='Post update date' # Дата обновления
    )

# replace(tzinfo=None) - sqlalchemy глючит при работе с UTC