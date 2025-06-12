from typing import Sequence, Optional, Any

from sqlalchemy import select, update, exists
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coefficient import Coefficient
from app.schemas.coefficient import CoefficientCreate, CoefficientUpdate


# ---------------------------------------------------------------------------
# GET-методы
# ---------------------------------------------------------------------------
async def get_coefficient(
    session: AsyncSession,
    coeff_id: int,
) -> Optional[Coefficient]:
    """Получить коэффициент по первичному `id`."""
    stmt = select(Coefficient).where(Coefficient.id == coeff_id)
    res = await session.scalars(stmt)
    return res.first()


async def get_all_coefficients(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = 100,
) -> Sequence[Coefficient]:
    """Вернуть все коэффициенты (с пагинацией)."""
    stmt = select(Coefficient).offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    res = await session.scalars(stmt.order_by(Coefficient.id))
    return res.all()


async def get_coefficient_field(
    session: AsyncSession,
    coeff_id: int,
    field_name: str,
) -> Optional[Any]:
    """Получить произвольное поле коэффициента."""
    if not hasattr(Coefficient, field_name):
        return None
    stmt = select(getattr(Coefficient, field_name)).where(Coefficient.id == coeff_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


#----------------------------------------#----------------------------------------
# Проверки и методы помощники
#----------------------------------------#----------------------------------------
async def coefficient_exists(
    session: AsyncSession,
    coeff_id: int,
) -> bool:
    """Проверяет, существует ли строка коэффициента по `id`."""
    stmt = select(exists().where(Coefficient.id == coeff_id))
    res = await session.execute(stmt)
    return res.scalar()