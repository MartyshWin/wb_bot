# Tasks
import logging
from typing import Sequence, Any, Optional

from sqlalchemy import select, update, delete, exists, func, distinct, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead


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

async def get_tasks_by_user_with_limit(
    session: AsyncSession,
    user_id: int,
    limit: int | None = None,
    offset: int | None = None,
) -> Sequence[Task]:
    """Возвращает задачи только по 10 (или другим лимитом) уникальным складам,
    и для каждой пары (warehouse_id, box_type_id) берёт запись с максимальным коэффициентом."""

    # Шаг 1: Получаем уникальные warehouse_id с лимитом
    wh_stmt = (
        select(distinct(Task.warehouse_id))
        .where(Task.user_id == user_id)
        .order_by(Task.created_at)
    )

    if limit is not None:
        wh_stmt = wh_stmt.limit(limit)
    if offset is not None:
        wh_stmt = wh_stmt.offset(offset)

    result = await session.execute(wh_stmt)
    warehouse_ids = [row[0] for row in result.all()]

    if not warehouse_ids:
        return []

    # Шаг 2: Получаем задачи с максимальным коэффициентом для каждой (warehouse, box_type) из выбранных складов
    subq = (
        select(
            Task.id,
            func.rank().over(
                partition_by=(Task.warehouse_id, Task.box_type_id),
                order_by=Task.coefficient.desc()
            ).label("rnk")
        )
        .where(
            Task.user_id == user_id,
            Task.warehouse_id.in_(warehouse_ids)
        )
        .subquery()
    )

    stmt = (
        select(Task)
        .join(subq, Task.id == subq.c.id)
        .where(subq.c.rnk == 1)
    )

    result = await session.scalars(stmt)
    return result.all()


async def get_unique_warehouses(session: AsyncSession, user_id: int) -> list[int]:
    """ID уникальных складов пользователя."""
    stmt = select(distinct(Task.warehouse_id)).where(Task.user_id == user_id)
    rows = await session.execute(stmt)
    return [row[0] for row in rows.fetchall()]

# ── Экспериментальные функции  ───────────────────────────────────────────
async def get_tasks_unique_by_warehouse(
        session: AsyncSession,
        user_id: int,
        warehouse_ids: list[int] | None = None
) -> Sequence[TaskRead]:
    """
    Возвращает по одной задаче на каждый уникальный warehouse_id (или паре warehouse_id + user_id),
    с максимальным коэффициентом. При наличии фильтра warehouse_ids — применяется он тоже.

    :param session: Асинхронная сессия базы данных.
    :param user_id: ID пользователя.
    :param warehouse_ids: Список ID складов (опционально).
    :return: Список TaskRead.
    """
    filters = [Task.user_id == user_id]
    if warehouse_ids:
        filters.append(Task.warehouse_id.in_(warehouse_ids))

    subq = (
        select(
            Task.id,
            func.row_number().over(
                partition_by=Task.warehouse_id,
                order_by=Task.coefficient.desc()
            ).label("rn")
        )
        .where(*filters)
        .subquery()
    )

    stmt = (
        select(Task)
        .join(subq, Task.id == subq.c.id)
        .where(subq.c.rn == 1)
    )

    result = await session.scalars(stmt)
    tasks: Sequence[Task] = result.all() # Объявляем ORM модель объекта Task
    return [TaskRead.model_validate(task) for task in tasks] # Превращаем из ORM в TaskRead


async def get_tasks_unique_by_warehouse_and_box_type(
    session: AsyncSession,
    user_id: int,
    warehouse_ids: list[int] | None = None
) -> Sequence[TaskRead]:
    """
    Возвращает по одной задаче на каждую уникальную пару (warehouse_id, box_type_id)
    у заданного пользователя, с наибольшим коэффициентом.
    При наличии фильтра warehouse_ids — выводятся задачи только для этого склада.
    """
    filters = [Task.user_id == user_id]
    if warehouse_ids:
        filters.append(Task.warehouse_id.in_(warehouse_ids))

    subq = (
        select(
            Task.id,
            func.row_number().over(
                partition_by=(Task.warehouse_id, Task.box_type_id),
                order_by=Task.coefficient.desc()
            ).label("rn")
        )
        .where(*filters)
        .subquery()
    )

    stmt = (
        select(Task)
        .join(subq, Task.id == subq.c.id)
        .where(subq.c.rn == 1)
    )

    result = await session.scalars(stmt)
    tasks: Sequence[Task] = result.all() # Объявляем ORM модель объекта Task
    return [TaskRead.model_validate(task) for task in tasks] # Превращаем из ORM в TaskRead

async def get_tasks_by_user_and_wh(session: AsyncSession, user_id: int, warehouse_ids: list[int]) -> Sequence[TaskRead]:
    """Все задачи, принадлежащие пользователю."""
    filters = [Task.user_id == user_id]
    if warehouse_ids:
        filters.append(Task.warehouse_id.in_(warehouse_ids))

    stmt = select(Task).where(*filters)
    result = await session.scalars(stmt)
    tasks: Sequence[Task] = result.all()  # Объявляем ORM модель объекта Task
    return [TaskRead.model_validate(task) for task in tasks]  # Превращаем из ORM в TaskRead
# ────────────────────────────────────────────────────────────────────────────


async def get_warehouses_with_alarm(session: AsyncSession, user_id: int) -> list[dict[str, int | bool]]:
    """
    Возвращает список складов пользователя с их флагом alarm.
    Пример: [{'warehouse_id': 123, 'alarm': True}, ...]
    """
    stmt = (
        select(Task.warehouse_id, Task.alarm)
        .where(Task.user_id == user_id)
        .group_by(Task.warehouse_id, Task.alarm)  # группируем, если есть дубли
    )
    rows = await session.execute(stmt)
    return [{"id": wid, "alarm": alarm} for wid, alarm in rows.fetchall()]

async def count_uniq_tasks_by_whs(session: AsyncSession, user_id: int) -> int:
    """Количество уникальных складов у пользователя."""
    stmt = select(func.count(distinct(Task.warehouse_id))).where(Task.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one()


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
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Ошибка при создании задачи: {e}", exc_info=True)
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
