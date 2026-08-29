from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class MonthTotals(BaseModel):
    month: date  # primeiro dia do mês
    total_income: Decimal
    total_expenses: Decimal
    net: Decimal  # receitas - despesas


class MonthComparison(BaseModel):
    current: MonthTotals
    previous: MonthTotals
    # current - previous (pode ser negativo).
    income_change: Decimal
    expenses_change: Decimal
    net_change: Decimal
    # Variação percentual face ao mês anterior. `None` quando o mês anterior foi 0
    # (dividir por zero não tem significado). Rácios de exibição — daí `float`.
    income_change_pct: float | None
    expenses_change_pct: float | None


class MonthlyTrend(BaseModel):
    # Do mês mais antigo para o mais recente.
    points: list[MonthTotals]
