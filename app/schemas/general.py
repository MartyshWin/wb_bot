from datetime import datetime, UTC
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, conint

from app.enums.general import TaskMode


class ResponseModel(BaseModel):
    status: Literal[True] = Field(default=True, description="Флаг успешного ответа (фиксирован на True)")
    text: str = Field(description="Короткое сообщение для пользователя/клиента", examples=["Операция выполнена успешно"])
    kb: Optional[Any] = Field(default=None, description="Клавиатура/меню", examples=["keyboard"])


class ResponseError(BaseModel):
    """
    Универсальный ответ-ошибка.
    Совместим с RFC 7807 (Problem Details), но короче и без verbosity.
    """
    status: Literal[False] = Field(default=False, description="Фиксированный флаг 'успех = False'")
    code: str = Field(examples=["WAREHOUSE_NOT_FOUND"], description="Машиночитаемый код ошибки")
    message: str = Field(examples=["Склад с указанным ID не найден"], description="Человекочитаемое сообщение")
    errors: Optional[list] = Field(default=None, description="Список детальных ошибок (валидация и пр.)")
    detail: Optional[Any] = Field(default=None, description="Произвольный объект/словарь с доп. данными")
    status_code: Optional[int] = Field(default=None, ge=100, le=599, examples=[404], description="HTTP-код (если нужен клиенту)")
    path: Optional[str] = Field(default=None, examples=["/api/v1/warehouses/314"], description="URL запроса")
    method: Optional[str] = Field(default=None, examples=["GET"], description="HTTP-метод запроса")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="ISO 8601 время (UTC)")
    trace_id: Optional[str] = Field(default=None, examples=["f5c1b1e0-4be1-48c7-b8f4-c5cdd7abc123"], description="Корреляционный ID для логов/трейсинга")

class ResponseWarehouses(BaseModel):
    warehouses: list[dict[str, int | str]]
    mode: str
    offset: int = Field(..., ge=0, description="Сколько записей пропустить от начала")
    limit: int = Field(..., gt=0, description="Размер страницы")
    total: int = Field(..., ge=0, description="Сколько всего складов")

    @property
    def page_index(self) -> int:  # 0-based
        return self.offset // self.limit

    @property
    def total_pages(self) -> int:  # 1-based
        return (self.total + self.limit - 1) // self.limit

class ResponseBoxTypes(BaseModel):
    selected: list[str] = Field(default_factory=list, description="Уже отмеченные типы")
    back: bool = Field(default=False, description="Пришли из режима редактирования")
    warehouse_id: int = Field(default=0, description="Бизнес-ID склада")
    page: int = Field(default=0, ge=0, description="Индекс текущей страницы")
    box_default: Optional[list[int]] = Field(default=None, description="Типы по умолчанию из задачи")
    mode: TaskMode = Field(default=TaskMode.FLEX, description="flex / mass")

class ResponseCoefs(BaseModel):
    selected: Optional[conint(ge=0, le=20)] = Field(None, description="Выбранный коэффициент (0‥20) или None")
    coef_default: conint(ge=0, le=20) = Field(0, description="Коэффициент по умолчанию из задачи")
    back: bool = Field(False, description="True, если вернулись из режима редактирования")
    warehouse_id: int = Field(0, description="Бизнес-ID склада")
    page: int = Field(0, ge=0, description="Индекс текущей страницы")
    mode: TaskMode = Field(TaskMode.FLEX, description="flex / mass")