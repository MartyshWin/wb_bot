from pydantic import Field
from typing import Optional
from pydantic import BaseModel


class PaginationMixin(BaseModel):
    offset: int = Field(..., ge=0, description="Сколько записей пропустить от начала")
    limit: int = Field(..., gt=0, description="Размер страницы")
    total: int = Field(..., ge=0, description="Общее количество записей")

    @property
    def page_index(self) -> int:
        return self.offset // self.limit

    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit