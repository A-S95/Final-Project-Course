import enum
import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DashboardScope(enum.StrEnum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"


class CategoryExpense(BaseModel):
    """Total gasto numa categoria dentro do mês. `owner_name` é `None` para despesas
    partilhadas (fundidas entre membros) ou na vista individual; caso contrário
    identifica de quem é, para não confundir categorias homónimas entre membros."""

    category_id: uuid.UUID
    name: str
    color: str | None
    total: Decimal
    owner_name: str | None = None


class DashboardSummary(BaseModel):
    month: date  # primeiro dia do mês (ex: 2026-08-01)
    # Se pediram "household" sem pertencer a um agregado, o service devolve "individual".
    scope: DashboardScope
    total_balance: Decimal  # saldo "agora", não do mês escolhido
    total_income: Decimal  # transferências nunca entram nestes totais
    total_expenses: Decimal
    net: Decimal  # total_income - total_expenses
    savings_rate: float | None  # (net/income)*100; None sem receitas no mês
    expenses_by_category: list[CategoryExpense]
    shared_expenses_total: Decimal  # soma das despesas marcadas is_shared
