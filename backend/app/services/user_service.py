from decimal import Decimal

from app.models.user import User


def update_profile(
    user: User, *, name: str, currency: str, monthly_income: Decimal | None
) -> User:
    user.name = name
    user.currency = currency
    user.monthly_income = monthly_income
    return user
