import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    account_id: uuid.UUID
    destination_account_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str | None = Field(default=None, max_length=200)
    date: date
    # Só tem efeito para quem pertence a um agregado — ver Transaction.is_shared.
    is_shared: bool = False


class TransactionUpdate(BaseModel):
    """Ao contrário de `AccountUpdate`/`CategoryUpdate`, aqui todos os campos são
    obrigatórios (não é um PATCH parcial por campo). `type`, `category_id` e
    `destination_account_id` têm invariantes cruzadas — uma transferência nunca tem
    categoria, uma receita/despesa nunca tem conta de destino — e permitir editar só
    um campo de cada vez tornaria ambíguo o que um `None` significa ao mudar de tipo
    (\"não mexer neste campo\" ou \"limpá-lo porque já não se aplica\"). Assume-se que a
    UI reenvia sempre o formulário completo ao editar uma transação.
    """

    account_id: uuid.UUID
    destination_account_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str | None = Field(default=None, max_length=200)
    date: date
    is_shared: bool = False


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    destination_account_id: uuid.UUID | None
    category_id: uuid.UUID | None
    type: TransactionType
    amount: Decimal
    description: str | None
    date: date
    is_shared: bool
    # `None` = sem recibo anexado; caso contrário, o Content-Type a esperar de
    # GET /transactions/{id}/receipt (a imagem/PDF em si não vai aqui).
    receipt_content_type: str | None
    created_at: datetime
    updated_at: datetime
