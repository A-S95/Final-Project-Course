import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.account import AccountType


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: AccountType
    # Sem `gt=0`: saldo pode ser negativo (cartão de crédito, descoberto).
    initial_balance: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    card_expiration_date: date | None = None  # só cartões físicos/pré-pagos
    card_plafond: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: AccountType | None = None
    initial_balance: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    # Nestes dois `null` é um destino válido; o service distingue "omitido" de
    # "enviado como null" via `model_fields_set`, não o padrão "None = não mexer".
    card_expiration_date: date | None = None
    card_plafond: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: AccountType
    initial_balance: Decimal
    current_balance: Decimal
    card_expiration_date: date | None
    card_plafond: Decimal | None
    created_at: datetime
    updated_at: datetime
