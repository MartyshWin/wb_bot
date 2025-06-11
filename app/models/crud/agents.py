# Bot
from typing import Sequence, Optional, Any

import re
from sqlalchemy import select, update, exists, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot import Bot         # ORM-модель
from app.schemas.bot import BotCreate  # Pydantic-схема (если понадобится)


#----------------------------------------#----------------------------------------
# Методы `get`
# Получение ботов
#----------------------------------------#----------------------------------------
async def get_bot_by_id(
        session: AsyncSession,
        bot_id: int
) -> Optional[Bot]:
    """
    Получение информации о боте по его ID.
    """
    stmt = select(Bot).where(Bot.bot_id == bot_id)
    result = await session.scalars(stmt)
    return result.first()


async def get_all_bots(
        session: AsyncSession
) -> Sequence[Bot]:
    """
    Получение информации обо всех ботах.
    """
    stmt = select(Bot)
    result = await session.scalars(stmt)
    return result.all()


async def get_bot_field(
        session: AsyncSession,
        bot_id: int,
        field_name: str
) -> Optional[Any]:
    """
    Получение значения произвольного поля из таблицы `bots`.
    """
    if not hasattr(Bot, field_name):
        return None

    stmt = select(getattr(Bot, field_name)).where(Bot.bot_id == bot_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


#----------------------------------------#----------------------------------------
# Методы `create`
# Создание ботов
#----------------------------------------#----------------------------------------
async def create_bot(
        session: AsyncSession,
        user_id: int,
        bot_id: int,
        api_token: str
) -> Optional[Bot]:
    """
    Добавление нового бота в базу данных.
    """
    bot = Bot(user_id=user_id, bot_id=bot_id, api_token=api_token)
    session.add(bot)
    try:
        await session.commit()
        await session.refresh(bot)
        return bot
    except SQLAlchemyError as e:
        await session.rollback()
        # logging.error(f"Ошибка при добавлении бота {bot_id}: {e}")
        return None


#----------------------------------------#----------------------------------------
# Методы `update`
# Обновление ботов
#----------------------------------------#----------------------------------------
async def update_bot_field(
        session: AsyncSession,
        bot_id: int,
        field_name: str,
        value: Any
) -> bool:
    """
    Обновление произвольного поля в записи бота.
    """
    # Проверяем имя поля на безопасность
    if not re.fullmatch(r"[a-zA-Z0-9_]+", field_name):
        return False
    if not hasattr(Bot, field_name):
        return False

    try:
        stmt = (
            update(Bot)
            .where(Bot.bot_id == bot_id)
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
async def bot_exists(
        session: AsyncSession,
        bot_id: int
) -> bool:
    """
    Проверяет, существует ли бот с указанным bot_id.
    """
    stmt = select(exists().where(Bot.bot_id == bot_id))
    result = await session.execute(stmt)
    return result.scalar()
