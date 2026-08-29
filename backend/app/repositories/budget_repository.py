import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType


def list_by_user_and_month(
    db: Session, user_id: uuid.UUID, period_month: date
) -> list[Budget]:
    return list(
        db.scalars(
            select(Budget)
            .where(Budget.user_id == user_id, Budget.period_month == period_month)
            .order_by(Budget.created_at)
        )
    )


def get_by_id_for_user(db: Session, budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget | None:
    return db.scalar(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
    )


def get_by_category_and_month(
    db: Session, *, user_id: uuid.UUID, category_id: uuid.UUID, period_month: date
) -> Budget | None:
    return db.scalar(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.period_month == period_month,
        )
    )


def create(
    db: Session,
    *,
    user_id: uuid.UUID,
    category_id: uuid.UUID,
    period_month: date,
    amount: Decimal,
) -> Budget:
    budget = Budget(
        user_id=user_id, category_id=category_id, period_month=period_month, amount=amount
    )
    db.add(budget)
    db.flush()
    return budget


def delete(db: Session, budget: Budget) -> None:
    db.delete(budget)


def spent_by_category(
    db: Session,
    user_id: uuid.UUID,
    *,
    month_start: date,
    next_month_start: date,
) -> dict[uuid.UUID, Decimal]:
    """Total de despesa por categoria no intervalo [month_start, next_month_start[.

    Devolve só as categorias que tiveram despesa — o service assume 0 para as que
    faltam.
    """
    stmt = (
        select(Transaction.category_id, func.sum(Transaction.amount))
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.category_id.is_not(None),
            Transaction.date >= month_start,
            Transaction.date < next_month_start,
        )
        .group_by(Transaction.category_id)
    )
    return {row[0]: row[1] for row in db.execute(stmt).all()}
