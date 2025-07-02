from datetime import datetime, UTC
from typing import Literal, Optional, Any, Union
from pydantic import BaseModel, Field, conint
from sqlalchemy import Sequence

from app.enums.general import TaskMode
from app.schemas.mixins.pagination import PaginationMixin
from app.schemas.task import TaskRead
from app.schemas.warehouse import WarehouseRead


class ResponseModel(BaseModel):
    status: bool = Field(default=True, description="Флаг успешного ответа (фиксирован на True)")
    text: str = Field(description="Короткое сообщение для пользователя/клиента", examples=["Операция выполнена успешно"])
    kb: Optional[Any] = Field(default=None, description="Клавиатура/меню", examples=["keyboard"])
    popup_text: Optional[str] = Field(default=None, description="Текст всплывающего окна")
    popup_alert: Optional[bool] = Field(default=False, description="Всплывающее окно с подтверждением или без него")
    type_edit: Optional[str] = Field(default=None, description="Тип редактирования (message или keyboard)") # edit_message_reply_markup()

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

class ResponseWarehouses(PaginationMixin):
    warehouses: Union[list[dict[str, int | str]], list[WarehouseRead]]
    mode: Optional[str] = None
    task_list: Optional[list[dict[str, int | bool]]] = None


class ResponseTasks(PaginationMixin):
    tasks: list[TaskRead]
    warehouses_names_list: Optional[Union[list[dict[str, int | str]], list[WarehouseRead]]] = None

class ResponseBoxTypes(BaseModel):
    selected: list[str] = Field(default_factory=list, description="Уже отмеченные типы")
    back: bool = Field(default=False, description="Пришли из режима редактирования")
    warehouse_id: int = Field(default=0, description="Бизнес-ID склада")
    page: int = Field(default=0, ge=0, description="Индекс текущей страницы")
    box_default: Optional[list[str]] = Field(default=None, description="Типы по умолчанию из задачи")
    mode: TaskMode = Field(default=TaskMode.MASS, description="flex / mass")

class ResponseCoefs(BaseModel):
    selected: Optional[conint(ge=0, le=20)] = Field(None, description="Выбранный коэффициент (0‥20) или None")
    coef_default: conint(ge=0, le=20) = Field(default=0, description="Коэффициент по умолчанию из задачи")
    back: bool = Field(default=False, description="Пришли из режима редактирования")
    warehouse_id: int = Field(default=0, description="Бизнес-ID склада")
    page: int = Field(default=0, ge=0, description="Индекс текущей страницы")
    mode: TaskMode = Field(default=TaskMode.MASS, description="flex / mass")