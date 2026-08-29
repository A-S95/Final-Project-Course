import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.dates import month_bounds
from app.core.exceptions import (
    BudgetAlreadyExistsError,
    BudgetCategoryInvalidError,
    BudgetNotFoundError,
)
from app.models.budget import Budget
from app.models.category import CategoryType
from app.repositories import budget_repository
from app.schemas.budget import BudgetRead
from app.services import category_service

_CENTS = Decimal("0.01")


def _to_read(budget: Budget, *, category_name: str, spent: Decimal) -> BudgetRead:
    spent = spent.quantize(_CENTS)
    remaining = (budget.amount - spent).quantize(_CENTS)
    percentage = round(float(spent / budget.amount * 100), 1) if budget.amount > 0 else 0.0
    return BudgetRead(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category_name,
        period_month=budget.period_month,
        amount=budget.amount,
        spent=spent,
        remaining=remaining,
        percentage=percentage,
    )


def _read_with_spent(db: Session, *, user_id: uuid.UUID, budget: Budget) -> BudgetRead:
    month_start, next_month_start = month_bounds(budget.period_month)
    spent_map = budget_repository.spent_by_category(
        db, user_id, month_start=month_start, next_month_start=next_month_start
    )
    category = category_service.get_category(db, user_id=user_id, category_id=budget.category_id)
    return _to_read(
        budget, category_name=category.name, spent=spent_map.get(budget.category_id, Decimal(0))
    )


def get_budget(db: Session, *, user_id: uuid.UUID, budget_id: uuid.UUID) -> Budget:
    budget = budget_repository.get_by_id_for_user(db, budget_id, user_id)
    if budget is None:
        raise BudgetNotFoundError
    return budget


def list_budgets(db: Session, *, user_id: uuid.UUID, period_month: date) -> list[BudgetRead]:
    month_start, next_month_start = month_bounds(period_month)
    budgets = budget_repository.list_by_user_and_month(db, user_id, month_start)
    spent_map = budget_repository.spent_by_category(
        db, user_id, month_start=month_start, next_month_start=next_month_start
    )
    reads = []
    for budget in budgets:
        category = category_service.get_category(
            db, user_id=user_id, category_id=budget.category_id
        )
        reads.append(
            _to_read(
                budget,
                category_name=category.name,
                spent=spent_map.get(budget.category_id, Decimal(0)),
            )
        )
    return reads


def create_budget(
    db: Session,
    *,
    user_id: uuid.UUID,
    category_id: uuid.UUID,
    period_month: date,
    amount: Decimal,
) -> BudgetRead:
    month_start, _ = month_bounds(period_month)

    # Levanta CategoryNotFoundError se a categoria não existir / não for do utilizador.
    category = category_service.get_category(db, user_id=user_id, category_id=category_id)
    if category.type != CategoryType.EXPENSE:
        raise BudgetCategoryInvalidError

    existing = budget_repository.get_by_category_and_month(
        db, user_id=user_id, category_id=category_id, period_month=month_start
    )
    if existing is not None:
        raise BudgetAlreadyExistsError

    budget = budget_repository.create(
        db,
        user_id=user_id,
        category_id=category_id,
        period_month=month_start,
        amount=amount,
    )
    return _read_with_spent(db, user_id=user_id, budget=budget)


def update_budget(
    db: Session, *, user_id: uuid.UUID, budget_id: uuid.UUID, amount: Decimal
) -> BudgetRead:
    budget = get_budget(db, user_id=user_id, budget_id=budget_id)
    budget.amount = amount
    db.flush()
    return _read_with_spent(db, user_id=user_id, budget=budget)


def delete_budget(db: Session, *, user_id: uuid.UUID, budget_id: uuid.UUID) -> None:
    budget = get_budget(db, user_id=user_id, budget_id=budget_id)
    budget_repository.delete(db, budget)
    db.flush()
