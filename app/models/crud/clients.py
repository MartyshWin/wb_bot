# Users
from typing import Sequence, Any, Coroutine, Optional

from sqlalchemy import update, exists, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

#----------------------------------------#----------------------------------------
# Методы `get`
# Получение пользователей
#----------------------------------------#----------------------------------------
async def get_user(
        session: AsyncSession,
        user_id: int
) -> Optional[User]:
    """
    Получить пользователя по полю user_id.
    """
    stmt = select(User).where(User.user_id == user_id)
    result = await session.scalars(stmt)
    return result.first()


async def get_all_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int | None = 100
) -> Sequence[User]:
    """
    Получить список всех пользователей с пагинацией.
    """
    stmt = select(User).offset(skip)
    if limit:
        stmt = stmt.limit(limit)
    result = await session.scalars(stmt.order_by(User.id))
    return result.all()


async def get_user_by_id(
    session: AsyncSession,
    user_id: int
) -> Optional[User]:
    """
    Получить пользователя по полю user_id.
    """
    stmt = select(User).where(User.user_id == user_id)
    result = await session.scalars(stmt)
    return result.first()

async def get_user_field_by_id(
        session: AsyncSession,
        user_id: int,
        field_name: str
) -> Optional[Any]:
    """
    Получить определенное поле пользователя по user_id
    """
    if not hasattr(User, field_name):
        return None

    stmt = select(getattr(User, field_name)).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

#----------------------------------------#----------------------------------------
# Методы `create`
# Создание пользователей
#----------------------------------------#----------------------------------------
async def create_user(
    session: AsyncSession,
    user_create: UserCreate,
) -> Optional[User]:
    """
    Создать пользователя
    """
    user = User(**user_create.model_dump())
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except SQLAlchemyError:
        await session.rollback()
        return None

#----------------------------------------#----------------------------------------
# Методы `update`
# Обновление пользователей
#----------------------------------------#----------------------------------------
async def update_user(
    session: AsyncSession,
    new_user: UserUpdate
) -> Optional[User]:
    """
    Обновить пользователя
    """
    try:
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
    except SQLAlchemyError:
        await session.rollback()
        return None


async def update_user_activity(
        session: AsyncSession,
        user_id: int,
        activity: str
) -> bool:
    """
    Обновляет поле activity
    """
    try:
        stmt = update(User).where(User.user_id == user_id).values(activity=activity)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await session.rollback()
        return False


async def assign_bot_to_user(
        session: AsyncSession,
        user_id: int,
        bot_id: int
) -> bool:
    """
    Устанавливает связь между пользователем и ботом, обновляя поле bot_id
    """
    try:
        stmt = update(User).where(User.user_id == user_id).values(bot_id=bot_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await session.rollback()
        return False


async def update_user_field(
        session: AsyncSession,
        user_id: int,
        field_name: str,
        value: Any
) -> bool:
    """
    Устанавливает значение value определенному полю, переданное в поле field_name
    """
    if not hasattr(User, field_name):
        return False

    try:
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values({field_name: value})
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await session.rollback()
        return False


#----------------------------------------#----------------------------------------
# Проверки и методы помощники
#----------------------------------------#----------------------------------------
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
