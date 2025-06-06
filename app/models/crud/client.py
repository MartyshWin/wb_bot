# User
from typing import Sequence, Any, Coroutine

from sqlalchemy import update, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select


from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_all_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> Sequence[User]:
    """
    Получить список всех пользователей с пагинацией.
    """
    stmt = (select(User).offset(skip).limit(limit).order_by(User.id))
    # .where(User.status != 'removed'))
    result = await session.scalars(stmt)
    return result.all()

async def get_user_by_id(
    session: AsyncSession,
    user_id: int
) -> User | None:
    """
    Получить пользователя по полю user_id.
    """
    stmt = select(User).where(User.user_id == user_id)
    result = await session.scalars(stmt)
    return result.first()

async def create_user(
    session: AsyncSession,
    user_create: UserCreate,
) -> User:
    user = User(**user_create.model_dump())
    session.add(user)
    await session.commit()
    return user

async def update_user(
    session: AsyncSession,
    new_user: UserUpdate
) -> User:
    stmt = (
        update(User)
        .where(User.user_id == new_user.user_id)
        .values(new_user.model_dump(exclude_none=True))
        .returning(User)
    )
    result = await session.execute(stmt)
    updated_user = result.scalar_one_or_none()

    await session.commit()
    return updated_user

async def user_exists_by_id(
    session: AsyncSession,
    user_id: int
) -> bool:
    """
    Проверяет, существует ли пользователь с указанным Telegram user_id.
    """
    stmt = select(exists().where(User.user_id == user_id))
    result = await session.execute(stmt)
    return result.scalar()