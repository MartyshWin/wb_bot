# Warehouses
from typing import Sequence, Optional, Any, List, Dict

from sqlalchemy import select, update, exists, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseUpdate,
)

# ---------------------------------------------------------------------------
# GET-методы
# ---------------------------------------------------------------------------
async def get_warehouse(session: AsyncSession, warehouse_id: int) -> Optional[Warehouse]:
    """Получить склад по его business-id (`warehouse_id`)."""
    stmt = select(Warehouse).where(Warehouse.warehouse_id == warehouse_id)
    res = await session.scalars(stmt)
    return res.first()


async def get_all_warehouses(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = 100,
) -> Sequence[Warehouse]:
    """Вернуть все склады (с учетом лимитов и смещений)."""
    stmt = select(Warehouse).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    res = await session.scalars(stmt.order_by(Warehouse.id))
    return res.all()


async def get_warehouses_by_ids(
    session: AsyncSession,
    warehouse_ids: Sequence[int],
) -> Sequence[Warehouse]:
    """Получить склады по списку business-id."""
    if not warehouse_ids:
        return []
    stmt = select(Warehouse).where(Warehouse.warehouse_id.in_(warehouse_ids))
    res = await session.scalars(stmt)
    return res.all()


async def get_warehouses_name_map(
    session: AsyncSession,
    warehouse_ids: Sequence[int],
) -> List[Dict[str, Any]]:
    """
    Вернуть список словарей {'warehouse_id': .., 'warehouse_name': ..}
    (тот же результат, что старый метод GetWarehousesByIds/FindWarehousesByIds).
    """
    rows = await get_warehouses_by_ids(session, warehouse_ids)
    return [
        {"id": w.warehouse_id, "name": w.warehouse_name}
        for w in rows
    ]


async def count_warehouses(session: AsyncSession) -> int:
    """Возвращает общее количество складов."""
    stmt = select(func.count()).select_from(Warehouse)
    res = await session.execute(stmt)
    return res.scalar_one()


async def get_warehouse_field(
    session: AsyncSession,
    warehouse_id: int,
    field_name: str,
) -> Optional[Any]:
    """Получить произвольное поле склада."""
    if not hasattr(Warehouse, field_name):
        return None
    stmt = select(getattr(Warehouse, field_name)).where(
        Warehouse.warehouse_id == warehouse_id
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()

#----------------------------------------#----------------------------------------
# Проверки и методы помощники
#----------------------------------------#----------------------------------------
async def warehouse_exists_by_id(session: AsyncSession, warehouse_id: int) -> bool:
    """Проверяет, существует ли склад с указанным warehouse_id."""
    stmt = select(exists().where(Warehouse.warehouse_id == warehouse_id))
    res = await session.execute(stmt)
    return res.scalar()

