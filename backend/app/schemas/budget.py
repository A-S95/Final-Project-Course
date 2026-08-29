import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    category_id: uuid.UUID
    # Qualquer dia do mês — o service normaliza para o dia 1.
    period_month: date
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetUpdate(BaseModel):
    """Só o valor é editável: a categoria e o mês identificam o orçamento (mudar
    qualquer um deles é, na prática, outro orçamento)."""

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetRead(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str
    period_month: date
    amount: Decimal
    # Calculados em runtime a partir das transações do mês — nunca colunas
    # (ver ARCHITECTURE.md secção 4).
    spent: Decimal
    remaining: Decimal  # amount - spent (negativo se ultrapassou o orçamento)
    percentage: float  # spent / amount * 100 (pode passar de 100)
