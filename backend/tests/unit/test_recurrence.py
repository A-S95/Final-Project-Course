from datetime import date

from app.models.recurring_expense import RecurringFrequency
from app.services.recurring_expense_service import advance

MONTHLY = RecurringFrequency.MONTHLY
YEARLY = RecurringFrequency.YEARLY


def test_monthly_advance_clamps_to_short_month() -> None:
    assert advance(date(2026, 1, 31), 31, MONTHLY) == date(2026, 2, 28)


def test_monthly_advance_restores_canonical_day_after_clamp() -> None:
    # Depois de 31/jan cair em 28/fev, março volta a ser 31 (usa o dia canónico).
    assert advance(date(2026, 2, 28), 31, MONTHLY) == date(2026, 3, 31)


def test_monthly_advance_rolls_over_the_year() -> None:
    assert advance(date(2026, 12, 15), 15, MONTHLY) == date(2027, 1, 15)


def test_yearly_advance_keeps_month_and_day() -> None:
    assert advance(date(2026, 3, 10), 10, YEARLY) == date(2027, 3, 10)


def test_yearly_advance_clamps_leap_day() -> None:
    assert advance(date(2024, 2, 29), 29, YEARLY) == date(2025, 2, 28)
