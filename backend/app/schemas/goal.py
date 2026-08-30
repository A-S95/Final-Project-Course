import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    current_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    deadline: date | None = None


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    current_amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    deadline: date | None = None  # null limpa o prazo, omitir mantém o atual (model_fields_set)


class GoalContribution(BaseModel):
    # Positivo adiciona, negativo corrige — o service rejeita se o total ficar < 0.
    amount: Decimal = Field(max_digits=12, decimal_places=2)


class GoalRead(BaseModel):
    id: uuid.UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    deadline: date | None
    # Calculados em runtime:
    remaining: Decimal  # max(target - current, 0)
    progress_percentage: float  # current / target * 100 (pode passar de 100)
    is_achieved: bool
    deadline_passed: bool  # prazo definido, no passado, e ainda não atingido
    months_until_deadline: int | None
    required_monthly_contribution: Decimal | None  # só com prazo futuro e não atingido
    created_at: datetime
    updated_at: datetime
