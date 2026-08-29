import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.account import AccountType


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: AccountType
    # NUMERIC(12,2) na BD — os limites aqui rejeitam com 422 em vez de deixar
    # rebentar um overflow no insert. Sem `gt=0`: uma conta pode ter saldo
    # negativo (cartão de crédito, descoberto).
    initial_balance: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: AccountType | None = None
    initial_balance: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: AccountType
    initial_balance: Decimal
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime
