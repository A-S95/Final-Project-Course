import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.dates import add_months, month_bounds
from app.models.transaction import TransactionType
from app.repositories import dashboard_repository
from app.schemas.analytics import MonthComparison, MonthlyTrend, MonthTotals

_CENTS = Decimal("0.01")

# Analytics é sempre da vista individual — o toggle de agregado familiar vive no
# dashboard (Fase 7). Estender a analytics ao agregado fica como iteração futura.


def _month_totals(db: Session, user_id: uuid.UUID, month_start: date) -> MonthTotals:
    _, next_start = month_bounds(month_start)
    income = dashboard_repository.sum_amount_by_type(
        db, [user_id], type=TransactionType.INCOME,
        month_start=month_start, next_month_start=next_start,
    )
    expenses = dashboard_repository.sum_amount_by_type(
        db, [user_id], type=TransactionType.EXPENSE,
        month_start=month_start, next_month_start=next_start,
    )
    return MonthTotals(
        month=month_start,
        total_income=income.quantize(_CENTS),
        total_expenses=expenses.quantize(_CENTS),
        net=(income - expenses).quantize(_CENTS),
    )


def _pct_change(current: Decimal, previous: Decimal) -> float | None:
    if previous == 0:
        return None
    return round(float((current - previous) / abs(previous) * 100), 1)


def get_comparison(
    db: Session, *, user_id: uuid.UUID, month: date | None = None
) -> MonthComparison:
    current_start = (month or date.today()).replace(day=1)
    previous_start = add_months(current_start, -1)

    current = _month_totals(db, user_id, current_start)
    previous = _month_totals(db, user_id, previous_start)

    return MonthComparison(
        current=current,
        previous=previous,
        income_change=(current.total_income - previous.total_income),
        expenses_change=(current.total_expenses - previous.total_expenses),
        net_change=(current.net - previous.net),
        income_change_pct=_pct_change(current.total_income, previous.total_income),
        expenses_change_pct=_pct_change(current.total_expenses, previous.total_expenses),
    )


def get_trend(
    db: Session, *, user_id: uuid.UUID, months: int, month: date | None = None
) -> MonthlyTrend:
    end_start = (month or date.today()).replace(day=1)
    points = [
        _month_totals(db, user_id, add_months(end_start, -(months - 1 - i)))
        for i in range(months)
    ]
    return MonthlyTrend(points=points)
