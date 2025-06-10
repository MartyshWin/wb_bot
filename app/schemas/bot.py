from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator


# Схема для создания бота
class BotCreate(BaseModel):
    user_id: int
    bot_id: int                            # Telegram-ID или иной уникальный ID бота
    api_token: str = Field(min_length=1)   # токен Telegram Bot API
    status: int = 1                        # 1 = активен, 0 = выключен

    @field_validator("api_token")
    def validate_telegram_token(cls, v: str) -> str:
        pattern = r"^\d{9,10}:[a-zA-Z0-9_-]{35}$"
        if not re.fullmatch(pattern, v):
            raise ValueError("Invalid Telegram Bot API token format. Expected: '1234567890:ABCdefGHIjkl...'")
        return v

# Схема для обновления бота отсутствует, так как не требуется
class BotUpdate(BaseModel):
    pass


# Схема для отдачи данных наружу (read-only)
class BotRead(BaseModel):
    user_id: int
    bot_id: int
    api_token: str
    status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Полная схема (внутреннее использование – все поля, включая метаданные)
class BotSchema(BaseModel):
    id: int
    user_id: int
    bot_id: int
    api_token: str
    status: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
