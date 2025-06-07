from typing import Sequence, Any, Optional

from sqlalchemy import select, update, delete, exists, func, distinct, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

__all__ = [
    # get
    "get_task",
    "get_tasks_by_user",
    "get_tasks_by_user_max_coef",
    "get_unique_warehouses",
    "get_task_field",
    # create
    "create_task",
    # update
    "update_task",
    "update_task_field",
    "toggle_alarm_state",
    "set_alarm_state_all",
    # delete
    "delete_tasks_by_user",
    "delete_tasks_by_user_and_warehouse",
    # misc
    "task_exists",
]

# ---------------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------------
async def get_task(session: AsyncSession, task_id: int) -> Optional[Task]:
    """Вернуть задачу по её первичному `id`."""
    stmt = select(Task).where(Task.id == task_id)
    result = await session.scalars(stmt)
    return result.first()


async def get_tasks_by_user(session: AsyncSession, user_id: int) -> Sequence[Task]:
    """Все задачи, принадлежащие пользователю."""
    stmt = select(Task).where(Task.user_id == user_id)
    result = await session.scalars(stmt)
    return result.all()


async def get_tasks_by_user_max_coef(
    session: AsyncSession,
    user_id: int,
    limit: int | None = None,
    offset: int | None = None,
) -> Sequence[Task]:
    """Задачи с максимальным `coefficient` для каждой пары (warehouse, box_type)."""
    subq = (
        select(
            Task.id,
            func.rank().over(
                partition_by=(Task.warehouse_id, Task.box_type_id),
                order_by=Task.coefficient.desc(),
            ).label("rnk"),
        )
        .where(Task.user_id == user_id)
        .subquery()
    )

    stmt = select(Task).join(subq, Task.id == subq.c.id).where(subq.c.rnk == 1)
    if limit is not None:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)

    result = await session.scalars(stmt)
    return result.all()


async def get_unique_warehouses(session: AsyncSession, user_id: int) -> list[int]:
    """ID уникальных складов пользователя."""
    stmt = select(distinct(Task.warehouse_id)).where(Task.user_id == user_id)
    rows = await session.execute(stmt)
    return [row[0] for row in rows.fetchall()]


async def get_task_field(session: AsyncSession, task_id: int, field_name: str) -> Any | None:
    """Получить произвольное поле задачи. Возвращает `None`, если поля нет."""
    if not hasattr(Task, field_name):
        return None
    stmt = select(getattr(Task, field_name)).where(Task.id == task_id)
    row = await session.execute(stmt)
    return row.scalar_one_or_none()

# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------
async def create_task(session: AsyncSession, data: TaskCreate) -> Optional[Task]:
    """Создать новую задачу и вернуть её."""
    task = Task(**data.model_dump())
    session.add(task)
    try:
        await session.commit()
        await session.refresh(task)
        return task
    except SQLAlchemyError:
        await session.rollback()
        return None

# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------
async def update_task(session: AsyncSession, task_id: int, data: TaskUpdate) -> Optional[Task]:
    """Частичное обновление задачи."""
    stmt = (
        update(Task)
        .where(Task.id == task_id)
        .values(data.model_dump(exclude_none=True))
        .returning(Task)
    )
    try:
        res = await session.execute(stmt)
        await session.commit()
        return res.scalar_one_or_none()
    except SQLAlchemyError:
        await session.rollback()
        return None


async def update_task_field(
        session: AsyncSession,
        task_id: int,
        field_name: str,
        value: Any
) -> bool:
    """Обновить одно поле задачи. Возвращает `True`, если запись затронута."""
    if not hasattr(Task, field_name):
        return False
    stmt = (
        update(Task)
        .where(Task.id == task_id)
        .values({field_name: value, "updated_at": func.current_timestamp()})
    )
    try:
        res = await session.execute(stmt)
        await session.commit()
        return res.rowcount > 0
    except SQLAlchemyError:
        await session.rollback()
        return False


async def toggle_alarm_state(session: AsyncSession, user_id: int, warehouse_id: int) -> int:
    """Инвертировать `alarm` для всех задач пользователя на складе. Возвращает кол-во строк."""
    stmt = text(
        """
        UPDATE tasks
        SET alarm = CASE WHEN alarm = 1 THEN 0 ELSE 1 END,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = :user_id AND warehouse_id = :warehouse_id
        """
    )
    try:
        res = await session.execute(stmt, {"user_id": user_id, "warehouse_id": warehouse_id})
        await session.commit()
        return res.rowcount
    except SQLAlchemyError:
        await session.rollback()
        return 0


async def set_alarm_state_all(session: AsyncSession, user_id: int, state: int) -> int:
    """Массовое обновление `alarm` для всех задач пользователя."""
    stmt = (
        update(Task)
        .where(Task.user_id == user_id)
        .values(alarm=state, updated_at=func.current_timestamp())
    )
    try:
        res = await session.execute(stmt)
        await session.commit()
        return res.rowcount
    except SQLAlchemyError:
        await session.rollback()
        return 0

# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------
async def delete_tasks_by_user(session: AsyncSession, user_id: int) -> int:
    """Удалить все задачи пользователя. Возвращает кол-во удалённых строк."""
    stmt = delete(Task).where(Task.user_id == user_id)
    try:
        res = await session.execute(stmt)
        await session.commit()
        return res.rowcount
    except SQLAlchemyError:
        await session.rollback()
        return 0


async def delete_tasks_by_user_and_warehouse(session: AsyncSession, user_id: int, warehouse_id: int) -> int:
    """Удалить задачи пользователя по конкретному складу."""
    stmt = delete(Task).where(Task.user_id == user_id, Task.warehouse_id == warehouse_id)
    try:
        res = await session.execute(stmt)
        await session.commit()
        return res.rowcount
    except SQLAlchemyError:
        await session.rollback()
        return 0

# ---------------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------------
async def task_exists(session: AsyncSession, task_id: int) -> bool:
    """Проверить, существует ли задача."""
    stmt = select(exists().where(Task.id == task_id))
    res = await session.execute(stmt)
    return res.scalar()
