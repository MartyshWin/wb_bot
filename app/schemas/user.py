from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Схема для создания пользователя (регистрация)
class UserCreate(BaseModel):
    user_id: int
    username: Optional[str] = None
    email: Optional[EmailStr] = Field(default=None, min_length=6, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    activity: Optional[str] = None
    bot_id: Optional[str] = None
    bot_status: bool = False  # например, по умолчанию

# Схема для обновления пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = Field(default=None, min_length=6, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    activity: Optional[str] = None
    bot_id: Optional[str] = None
    bot_status: Optional[bool] = None

# Схема для возвращения данных о пользователе
class UserRead(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    email: Optional[EmailStr] = Field(default=None, min_length=6, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    activity: Optional[str] = None
    bot_id: Optional[str] = None
    bot_status: bool
    created_at: datetime
    updated_at: datetime

# Общая схема пользователя
class UserSchema(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    email: Optional[EmailStr] = Field(default=None, min_length=6, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    activity: Optional[str] = None
    bot_id: Optional[str] = None
    bot_status: bool
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)