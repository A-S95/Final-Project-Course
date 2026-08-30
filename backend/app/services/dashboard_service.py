import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.dates import month_bounds
from app.models.transaction import TransactionType
from app.repositories import dashboard_repository, household_repository
from app.schemas.dashboard import CategoryExpense, DashboardScope, DashboardSummary

_CENTS = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    """Normaliza para 2 casas decimais — quando não há transações, o `COALESCE(..., 0)`
    do Postgres devolve um inteiro, e queremos que a API seja sempre `0.00`, não `0`."""
    return value.quantize(_CENTS)


def _savings_rate(income: Decimal, net: Decimal) -> float | None:
    if income <= 0:
        return None
    return round(float(net / income * 100), 1)


def _resolve_scope(
    db: Session, user_id: uuid.UUID, scope: DashboardScope
) -> tuple[DashboardScope, list[uuid.UUID]]:
    """Traduz o `scope` pedido numa lista de `user_id` a agregar.

    Se pediram "household" mas o utilizador não pertence a nenhum agregado, cai-se
    graciosamente na vista individual (a UI só mostra o toggle quando há agregado,
    mas a API não deve rebentar se for chamada à mão)."""
    if scope == DashboardScope.HOUSEHOLD:
        membership = household_repository.get_membership_for_user(db, user_id)
        if membership is not None:
            return DashboardScope.HOUSEHOLD, household_repository.member_user_ids(
                db, membership.household_id
            )
    return DashboardScope.INDIVIDUAL, [user_id]


def get_summary(
    db: Session,
    *,
    user_id: uuid.UUID,
    month: date | None = None,
    scope: DashboardScope = DashboardScope.INDIVIDUAL,
) -> DashboardSummary:
    month_start, next_month_start = month_bounds(month or date.today())
    resolved_scope, user_ids = _resolve_scope(db, user_id, scope)

    total_income = dashboard_repository.sum_amount_by_type(
        db,
        user_ids,
        type=TransactionType.INCOME,
        month_start=month_start,
        next_month_start=next_month_start,
    )
    total_expenses = dashboard_repository.sum_amount_by_type(
        db,
        user_ids,
        type=TransactionType.EXPENSE,
        month_start=month_start,
        next_month_start=next_month_start,
    )
    net = total_income - total_expenses

    breakdown = [
        CategoryExpense(
            category_id=row[0],
            name=row[1],
            color=row[2],
            total=_money(row[3]),
            owner_name=None if row[4] else row[5],  # partilhada (row[4]) já vem fundida
        )
        for row in dashboard_repository.expenses_by_category(
            db,
            user_ids,
            month_start=month_start,
            next_month_start=next_month_start,
            group_by_name=resolved_scope == DashboardScope.HOUSEHOLD,
        )
    ]
    shared_expenses_total = dashboard_repository.sum_shared_expenses(
        db, user_ids, month_start=month_start, next_month_start=next_month_start
    )

    return DashboardSummary(
        month=month_start,
        scope=resolved_scope,
        total_balance=_money(dashboard_repository.total_balance(db, user_ids)),
        total_income=_money(total_income),
        total_expenses=_money(total_expenses),
        net=_money(net),
        savings_rate=_savings_rate(total_income, net),
        expenses_by_category=breakdown,
        shared_expenses_total=_money(shared_expenses_total),
    )
