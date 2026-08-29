from datetime import date

from app.core.dates import add_months, month_bounds


def test_add_months_forward() -> None:
    assert add_months(date(2026, 8, 15), 3) == date(2026, 11, 1)


def test_add_months_backward_across_year() -> None:
    assert add_months(date(2026, 2, 10), -3) == date(2025, 11, 1)


def test_add_months_forward_across_year() -> None:
    assert add_months(date(2026, 11, 1), 2) == date(2027, 1, 1)


def test_add_months_zero_normalizes_to_first_of_month() -> None:
    assert add_months(date(2026, 6, 20), 0) == date(2026, 6, 1)


def test_month_bounds_is_semi_open() -> None:
    assert month_bounds(date(2026, 8, 27)) == (date(2026, 8, 1), date(2026, 9, 1))


def test_month_bounds_december_rolls_over() -> None:
    assert month_bounds(date(2026, 12, 5)) == (date(2026, 12, 1), date(2027, 1, 1))
