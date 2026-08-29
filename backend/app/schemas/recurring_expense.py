import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.recurring_expense import RecurringFrequency


class RecurringExpenseCreate(BaseModel):
    account_id: uuid.UUID
    category_id: uuid.UUID
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    frequency: RecurringFrequency
    # Primeira ocorrência. O `day_of_month` é derivado desta data (ver modelo).
    next_occurrence: date
    active: bool = True


class RecurringExpenseUpdate(BaseModel):
    account_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    frequency: RecurringFrequency | None = None
    next_occurrence: date | None = None
    active: bool | None = None


class RecurringExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    account_name: str
    category_id: uuid.UUID
    category_name: str
    description: str
    amount: Decimal
    frequency: RecurringFrequency
    day_of_month: int
    next_occurrence: date
    active: bool
    # `next_occurrence <= hoje` e `active` — ou seja, tem transações por gerar.
    is_due: bool
    created_at: datetime
    updated_at: datetime


class RecurringRunResult(BaseModel):
    generated: int
